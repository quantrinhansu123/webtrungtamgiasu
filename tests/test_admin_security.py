import hashlib
import hmac
import json
import base64
import urllib.parse
from io import BytesIO
from pathlib import Path

import pytest
from flask import Flask
from itsdangerous import BadSignature
from PIL import Image

from admin import server


@pytest.fixture(autouse=True)
def reset_security_state(monkeypatch):
    original = {
        "SESSION_COOKIE_SECURE": server.app.config["SESSION_COOKIE_SECURE"],
        "MAX_IMAGE_UPLOAD_BYTES": server.app.config["MAX_IMAGE_UPLOAD_BYTES"],
        "LOGIN_RATE_LIMIT": server.app.config["LOGIN_RATE_LIMIT"],
        "LOGIN_RATE_WINDOW_SECONDS": server.app.config[
            "LOGIN_RATE_WINDOW_SECONDS"
        ],
    }
    server.app.config.update(
        TESTING=True,
        SESSION_COOKIE_SECURE=False,
        MAX_IMAGE_UPLOAD_BYTES=server.MAX_IMAGE_UPLOAD_BYTES,
        LOGIN_RATE_LIMIT=server.LOGIN_RATE_LIMIT,
        LOGIN_RATE_WINDOW_SECONDS=server.LOGIN_RATE_WINDOW_SECONDS,
    )
    with server._LOGIN_ATTEMPTS_LOCK:
        server._LOGIN_ATTEMPTS.clear()
    monkeypatch.delenv("CMS_DRIVE_FOLDER_URL", raising=False)
    yield
    server.app.config.update(original)
    with server._LOGIN_ATTEMPTS_LOCK:
        server._LOGIN_ATTEMPTS.clear()


@pytest.fixture
def client():
    return server.app.test_client()


def login(client, monkeypatch):
    monkeypatch.setattr(
        server,
        "credentials_valid",
        lambda username, password: username == "admin" and password == "correct",
    )
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "correct"},
    )
    assert response.status_code == 200
    return response.get_json()["csrf_token"], response


def raster_bytes(image_format="PNG", size=(3, 2)):
    buffer = BytesIO()
    Image.new("RGB", size, (31, 103, 180)).save(buffer, format=image_format)
    return buffer.getvalue()


def test_old_public_secret_cannot_forge_admin_cookie(client, monkeypatch):
    monkeypatch.delenv("CMS_PASSWORD", raising=False)
    old_secret = b"tri-viet-cms-local-secret"
    auth_material = server.credential_auth_material(server.load_config())
    forged_auth_version = hmac.new(
        old_secret,
        auth_material.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    forged_app = Flask("forged-session")
    forged_app.secret_key = old_secret
    serializer = forged_app.session_interface.get_signing_serializer(forged_app)
    forged_cookie = serializer.dumps(
        {
            "logged_in": True,
            "username": "admin",
            "csrf_token": "x" * 43,
            "auth_version": forged_auth_version,
        }
    )
    client.set_cookie(
        server.app.config["SESSION_COOKIE_NAME"],
        forged_cookie,
    )
    active_serializer = server.app.session_interface.get_signing_serializer(
        server.app
    )
    with pytest.raises(BadSignature):
        active_serializer.loads(forged_cookie)

    response = client.get("/api/me")

    assert response.status_code == 200
    assert response.get_json() == {"logged_in": False}


def test_password_headers_are_not_an_authentication_bypass(client, monkeypatch):
    monkeypatch.setattr(server, "credentials_valid", lambda *_args: True)

    response = client.get(
        "/api/me",
        headers={
            "X-CMS-Username": "admin",
            "X-CMS-Password": "correct",
        },
    )

    assert response.get_json() == {"logged_in": False}


def test_login_issues_httponly_cookie_and_csrf_is_required(client, monkeypatch):
    csrf_token, login_response = login(client, monkeypatch)
    cookie = login_response.headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Strict" in cookie

    missing = client.post("/api/logout")
    assert missing.status_code == 403
    assert client.get("/api/me").get_json()["logged_in"] is True

    wrong = client.post(
        "/api/logout",
        headers={"X-CSRF-Token": "not-the-session-token"},
    )
    assert wrong.status_code == 403

    accepted = client.post(
        "/api/logout",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert accepted.status_code == 200
    assert client.get("/api/me").get_json() == {"logged_in": False}


def test_password_change_invalidates_current_and_other_sessions(monkeypatch):
    monkeypatch.delenv("CMS_PASSWORD", raising=False)
    active_config = {
        "username": "admin",
        "password_hash": "old-password-hash",
        "site_name": "Trí Việt",
        "logo": "/giasubinhminh.com/wp-content/uploads/logo.png",
        "hotline1": "0901 234 567",
        "hotline2": "0909 876 543",
        "feedback_images": server.DEFAULT_FEEDBACK_IMAGES,
    }
    monkeypatch.setattr(
        server,
        "load_config",
        lambda fresh=False: active_config,
    )

    def mutate_config(mutator, **_kwargs):
        return server.apply_config_mutator(active_config, mutator)

    monkeypatch.setattr(server, "mutate_config_atomic", mutate_config)
    first_client = server.app.test_client()
    second_client = server.app.test_client()
    first_csrf, _ = login(first_client, monkeypatch)
    login(second_client, monkeypatch)

    changed = first_client.put(
        "/api/settings",
        headers={"X-CSRF-Token": first_csrf},
        json={"new_password": "replacement-password"},
    )

    assert changed.status_code == 200
    assert changed.get_json()["reauthenticate"] is True
    assert first_client.get("/api/me").get_json() == {"logged_in": False}
    assert second_client.get("/api/me").get_json() == {"logged_in": False}


def test_logout_clears_only_current_cookie_without_persisting(monkeypatch):
    monkeypatch.delenv("CMS_PASSWORD", raising=False)
    active_config = {
        "username": "admin",
        "password_hash": "unchanged-password-hash",
        "session_epoch": "before-logout",
    }
    monkeypatch.setattr(
        server,
        "load_config",
        lambda fresh=False: active_config,
    )

    def unexpected_persistence(*_args, **_kwargs):
        raise AssertionError("Logout must not persist or publish anything")

    monkeypatch.setattr(server, "save_config", unexpected_persistence)
    monkeypatch.setattr(server, "mutate_config_atomic", unexpected_persistence)
    monkeypatch.setattr(server, "_github_request", unexpected_persistence)
    original_client = server.app.test_client()
    replay_client = server.app.test_client()
    csrf_token, _ = login(original_client, monkeypatch)
    cookie_name = server.app.config["SESSION_COOKIE_NAME"]
    copied_cookie = original_client.get_cookie(cookie_name).value

    logged_out = original_client.post(
        "/api/logout",
        headers={"X-CSRF-Token": csrf_token},
    )
    replay_client.set_cookie(cookie_name, copied_cookie)

    assert logged_out.status_code == 200
    assert active_config["session_epoch"] == "before-logout"
    assert original_client.get("/api/me").get_json() == {"logged_in": False}
    assert replay_client.get("/api/me").get_json()["logged_in"] is True


def test_login_rate_limit_returns_retry_after(client, monkeypatch):
    monkeypatch.setattr(server, "credentials_valid", lambda *_args: False)
    server.app.config.update(LOGIN_RATE_LIMIT=2, LOGIN_RATE_WINDOW_SECONDS=60)

    for _ in range(2):
        response = client.post(
            "/api/login",
            json={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401

    limited = client.post(
        "/api/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert limited.status_code == 429
    assert int(limited.headers["Retry-After"]) >= 1


@pytest.mark.parametrize(
    "page_id",
    [
        "../admin/index.html",
        r"..\admin\index.html",
        "%2e%2e/admin/index.html",
        "%252e%252e/admin/index.html",
        "/absolute/index.html",
        "C:/Windows/index.html",
        "safe/../../admin/index.html",
        ".git/index.html",
    ],
)
def test_editable_page_rejects_noncanonical_paths(page_id):
    assert server.is_editable_page(page_id) is False


def test_public_catch_all_cannot_read_repository_files(client):
    for path in (
        "/admin/config.json",
        "/requirements.txt",
        "/.git/config",
        "/giasubinhminh.com/%252e%252e/admin/config.json",
        "/giasubinhminh.com/.git/config",
        "/giasubinhminh.com/wp-admin/index.html",
        "/giasubinhminh.com/wp-login.php",
        "/giasubinhminh.com/wp-login.html",
    ):
        response = client.get(path)
        assert response.status_code == 404
        assert b"password_hash" not in response.data


def test_authenticated_page_endpoint_rejects_encoded_traversal(client, monkeypatch):
    login(client, monkeypatch)

    response = client.get("/api/pages/%252e%252e/admin/index.html")

    assert response.status_code in {400, 404}
    assert b"password_hash" not in response.data


@pytest.mark.parametrize(
    ("contents", "filename"),
    [
        (b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", "payload.svg"),
        (b"not really a jpeg", "payload.jpg"),
        (raster_bytes("PNG"), "mismatch.jpg"),
    ],
)
def test_upload_rejects_unsafe_or_invalid_images(
    client,
    monkeypatch,
    contents,
    filename,
):
    csrf_token, _ = login(client, monkeypatch)
    published = []
    auth_config = server.load_config()
    monkeypatch.setattr(
        server,
        "load_config",
        lambda fresh=False: auth_config,
    )
    monkeypatch.setattr(server, "running_on_vercel", lambda: True)
    monkeypatch.setattr(server, "session_secret_configured", lambda: True)
    monkeypatch.setattr(server, "github_enabled", lambda: True)
    monkeypatch.setattr(
        server,
        "github_upsert_file",
        lambda *args, **kwargs: published.append((args, kwargs)),
    )

    response = client.post(
        "/api/media/upload",
        headers={"X-CSRF-Token": csrf_token},
        data={"file": (BytesIO(contents), filename)},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert published == []


def test_upload_rejects_body_over_image_limit(client, monkeypatch):
    csrf_token, _ = login(client, monkeypatch)
    server.app.config["MAX_IMAGE_UPLOAD_BYTES"] = 32

    response = client.post(
        "/api/media/upload",
        headers={"X-CSRF-Token": csrf_token},
        data={"file": (BytesIO(b"x" * 33), "large.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "giới hạn" in response.get_json()["error"]


def test_valid_raster_upload_is_published_after_validation(client, monkeypatch):
    csrf_token, _ = login(client, monkeypatch)
    published = []
    auth_config = server.load_config()
    monkeypatch.setattr(
        server,
        "load_config",
        lambda fresh=False: auth_config,
    )
    monkeypatch.setattr(server, "running_on_vercel", lambda: True)
    monkeypatch.setattr(server, "session_secret_configured", lambda: True)
    monkeypatch.setattr(server, "github_enabled", lambda: True)
    monkeypatch.setattr(
        server,
        "github_upsert_file",
        lambda *args, **kwargs: published.append((args, kwargs)),
    )
    raw = raster_bytes("PNG", (3, 2))

    response = client.post(
        "/api/media/upload",
        headers={"X-CSRF-Token": csrf_token},
        data={"file": (BytesIO(raw), "valid.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    body = response.get_json()
    assert (body["width"], body["height"]) == (3, 2)
    assert body["path"].endswith(".png")
    assert len(published) == 1
    assert published[0][0][0].startswith(
        "giasubinhminh.com/wp-content/uploads/cms/"
    )
    assert published[0][0][1] == raw
    assert published[0][1]["binary"] is True


def test_rich_text_and_image_fields_block_stored_xss():
    source = """
    <html><head><title>Old</title></head><body>
      <h1 class="entry-title">Old heading</h1>
      <div class="entry-image"><img src="wp-content/uploads/old.png"></div>
      <div class="entry-content single-page"><p>Old content</p></div>
    </body></html>
    """
    malicious_heading = '<img src=x onerror="alert(1)">'
    malicious_content = """
      <script>alert(1)</script>
      <p onclick="alert(1)" style="background-image:url(javascript:alert(1));color:red">
        Safe <strong>formatting</strong>
        <a href="javascript:alert(1)" target="_blank">bad link</a>
        <img src="javascript:alert(1)" onerror="alert(1)">
      </p>
    """

    updated = server.apply_page_updates(
        source,
        {
            "heading": malicious_heading,
            "content": malicious_content,
        },
    )
    parsed = server.BeautifulSoup(updated, "html.parser")
    serialized = str(parsed).casefold()

    assert parsed.select_one("h1.entry-title").get_text() == malicious_heading
    assert parsed.select_one("script") is None
    entry = parsed.select_one(".entry-content")
    assert all(
        not attribute.casefold().startswith("on")
        for tag in entry.find_all(True)
        for attribute in tag.attrs
    )
    assert "javascript:" not in str(entry).casefold()
    assert "background-image" not in serialized
    assert parsed.select_one("strong").get_text() == "formatting"

    with pytest.raises(ValueError):
        server.apply_page_updates(
            source,
            {"thumbnail": "javascript:alert(1)"},
        )


def test_homepage_css_image_rejects_style_breakout():
    html = (
        "<style>#banner-75206964 .bg.bg-loaded "
        "{background-image:url(old.png)}</style>"
    )

    with pytest.raises(ValueError):
        server.replace_css_bg(
            html,
            "banner-75206964",
            "x);}</style><script>alert(1)</script>",
        )


def test_homepage_get_uses_canonical_config_logo(client, monkeypatch):
    config = {
        "username": "admin",
        "password_hash": "test-hash",
        "logo": "/giasubinhminh.com/wp-content/uploads/canonical.png",
    }
    homepage = """
    <html><head><title>Home</title></head><body>
      <div id="logo"><img class="header_logo"
        src="/giasubinhminh.com/wp-content/uploads/stale.png"></div>
    </body></html>
    """
    monkeypatch.setattr(server, "load_config", lambda fresh=False: config)
    monkeypatch.setattr(server, "read_page_file", lambda *_args, **_kwargs: homepage)
    login(client, monkeypatch)

    response = client.get("/api/homepage")

    assert response.status_code == 200
    assert response.get_json()["logo"] == config["logo"]


def test_homepage_put_synchronizes_static_and_public_logo(client, monkeypatch):
    old_logo = "/giasubinhminh.com/wp-content/uploads/old.png"
    new_logo = "/giasubinhminh.com/wp-content/uploads/new.png"
    config = {
        "username": "admin",
        "password_hash": "test-hash",
        "logo": old_logo,
        "feedback_images": server.DEFAULT_FEEDBACK_IMAGES,
    }
    homepage = f"""
    <html><head><title>Home</title></head><body>
      <div id="logo"><img class="header_logo" src="{old_logo}"></div>
    </body></html>
    """
    transaction = {}
    monkeypatch.setattr(server, "load_config", lambda fresh=False: config)

    def mutate_config(mutator, **kwargs):
        updated = server.apply_config_mutator(config, mutator)
        extra_builder = kwargs["extra_changes_builder"]
        transaction.update(
            extra_builder(
                updated,
                lambda path: (
                    homepage.encode("utf-8")
                    if path == server.HOMEPAGE_REPO_PATH
                    else b""
                ),
            )
        )
        transaction["publish_public"] = kwargs["publish_public"]
        return updated

    monkeypatch.setattr(server, "mutate_config_atomic", mutate_config)
    csrf_token, _ = login(client, monkeypatch)

    response = client.put(
        "/api/homepage",
        headers={"X-CSRF-Token": csrf_token},
        json={"logo": new_logo},
    )

    assert response.status_code == 200
    assert config["logo"] == new_logo
    assert transaction["publish_public"] is True
    assert new_logo in transaction[server.HOMEPAGE_REPO_PATH]


def test_public_site_config_has_exact_allowlist_and_all_feedback_items():
    config = {
        "username": "admin",
        "password": "plaintext-must-not-leak",
        "password_hash": "hash-must-not-leak",
        "address1": "private address",
        "github_token": "token-must-not-leak",
        "site_name": "Trí Việt",
        "logo": "/giasubinhminh.com/wp-content/uploads/logo.png",
        "hotline1": "0901 234 567",
        "hotline2": "0909 876 543",
        "feedback_images": server.DEFAULT_FEEDBACK_IMAGES,
        "homepage_feedback_images": server.DEFAULT_HOMEPAGE_FEEDBACK_IMAGES,
    }

    public = server.build_public_site_config(config)
    serialized = json.dumps(public)

    assert set(public) == {
        "site_name",
        "logo",
        "hotline1",
        "hotline2",
        "feedback_images",
        "homepage_feedback_images",
    }
    assert len(public["feedback_images"]) == server.FEEDBACK_IMAGE_COUNT
    assert (
        len(public["homepage_feedback_images"])
        == server.HOMEPAGE_FEEDBACK_IMAGE_COUNT
    )
    assert all(set(item) == {"url", "alt"} for item in public["feedback_images"])
    assert all(
        set(item) == {"url", "alt"}
        for item in public["homepage_feedback_images"]
    )
    for secret in (
        "plaintext-must-not-leak",
        "hash-must-not-leak",
        "private address",
        "token-must-not-leak",
    ):
        assert secret not in serialized


def test_public_runtime_embeds_config_without_fetching_blocked_json():
    config = {
        "site_name": "Trí Việt toàn website",
        "logo": "/giasubinhminh.com/wp-content/uploads/logo.png",
        "hotline1": "0901 234 567",
        "hotline2": "0909 876 543",
        "feedback_images": server.DEFAULT_FEEDBACK_IMAGES,
        "homepage_feedback_images": server.DEFAULT_HOMEPAGE_FEEDBACK_IMAGES,
    }

    runtime = server.render_public_site_runtime(config)

    assert "Trí Việt toàn website" in runtime
    assert "__SITE_CONFIG_JSON__" not in runtime
    assert "window.fetch" not in runtime
    assert ".testimonial-collage img" in runtime
    assert "#parent-feedback-gallery" in runtime
    assert "updateTextbookCovers" in runtime
    assert "initializeParentRequestCarousel" in runtime
    assert "parentRequestImageCount = 115" in runtime
    assert "parentRequestAutoplayDelay = 5000" in runtime
    assert "yeu-cau-tim-gia-su/yeu-cau-tim-gia-su-" in runtime
    assert "initializeRealActivityNews" in runtime
    assert runtime.count("hoat-dong-thuc-te/hoat-dong-tri-viet-") == 7
    assert "updateTuitionTables" in runtime
    for tuition_rate in (
        "120.000 – 200.000",
        "150.000 – 250.000",
        "200.000 – 300.000",
        "250.000 – 400.000",
        "350.000 – 500.000",
    ):
        assert tuition_rate in runtime
    for subject in ("ngu-van", "hoa-hoc", "vat-ly"):
        for grade in (10, 11, 12):
            assert (
                f"sach-giao-khoa-moi/{subject}-{grade}-gdpt-2018"
                in runtime
            )


def test_feedback_api_saves_homepage_and_shared_galleries(
    client,
    monkeypatch,
):
    config = {
        "username": "admin",
        "password_hash": "test-hash",
    }
    saved = []
    monkeypatch.setattr(server, "load_config", lambda fresh=False: config)

    def mutate_config(mutator, **kwargs):
        updated = server.apply_config_mutator(config, mutator)
        saved.append((dict(updated), kwargs))
        return updated

    monkeypatch.setattr(server, "mutate_config_atomic", mutate_config)
    csrf_token, _ = login(client, monkeypatch)

    response = client.put(
        "/api/feedback",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "images": server.DEFAULT_FEEDBACK_IMAGES,
            "homepage_images": server.DEFAULT_HOMEPAGE_FEEDBACK_IMAGES,
        },
    )

    assert response.status_code == 200
    assert (
        len(saved[0][0]["feedback_images"])
        == server.FEEDBACK_IMAGE_COUNT
    )
    assert (
        len(saved[0][0]["homepage_feedback_images"])
        == server.HOMEPAGE_FEEDBACK_IMAGE_COUNT
    )
    assert saved[0][1]["publish_public"] is True


def test_github_config_transaction_retries_and_publishes_one_visible_commit(
    monkeypatch,
):
    old_logo = "/giasubinhminh.com/wp-content/uploads/old.png"
    new_logo = "/giasubinhminh.com/wp-content/uploads/new.png"
    initial_config = {
        "username": "admin",
        "password_hash": "original-password-hash",
        "site_name": "Trí Việt",
        "logo": old_logo,
        "hotline1": "0901 234 567",
        "hotline2": "0909 876 543",
        "feedback_images": server.DEFAULT_FEEDBACK_IMAGES,
        "homepage_feedback_images": server.DEFAULT_HOMEPAGE_FEEDBACK_IMAGES,
    }
    concurrent_config = {
        **initial_config,
        "password_hash": "concurrent-password-hash",
        "session_epoch": "concurrent-credential-version",
    }
    homepage = (
        "<html><body><div id='logo'>"
        f"<img class='header_logo' src='{old_logo}'>"
        "</div></body></html>"
    )
    initial_files = {
        server.ADMIN_CONFIG_REPO_PATH: (
            json.dumps(initial_config).encode("utf-8")
        ),
        server.PUBLIC_CONFIG_REPO_PATH: b"old-public-config",
        server.PUBLIC_RUNTIME_REPO_PATH: b"old-public-runtime",
        server.HOMEPAGE_REPO_PATH: homepage.encode("utf-8"),
    }
    state = {
        "visible_head": "head-1",
        "patch_attempts": 0,
        "successful_ref_updates": 0,
        "blob_number": 0,
        "tree_number": 0,
        "commit_number": 0,
    }
    snapshots = {"head-1": dict(initial_files)}
    head_trees = {"head-1": "tree-head-1"}
    tree_files = {"tree-head-1": dict(initial_files)}
    blobs = {}
    commit_files = {}
    commit_parents = {}
    tree_path_sets = []
    visible_before_ref_updates = []
    calls = []

    def fake_github_request(method, url, payload=None):
        calls.append((method, url, payload))
        parsed = urllib.parse.urlsplit(url)
        api_path = parsed.path

        if method == "GET" and "/git/ref/heads/" in api_path:
            return {"object": {"sha": state["visible_head"]}}

        if method == "GET" and "/git/commits/" in api_path:
            commit_sha = urllib.parse.unquote(api_path.rsplit("/", 1)[-1])
            return {"tree": {"sha": head_trees[commit_sha]}}

        if method == "GET" and "/contents/" in api_path:
            repo_path = urllib.parse.unquote(
                api_path.split("/contents/", 1)[1]
            )
            ref = urllib.parse.parse_qs(parsed.query)["ref"][0]
            raw = snapshots[ref][repo_path]
            return {
                "content": base64.b64encode(raw).decode("ascii"),
                "sha": hashlib.sha1(raw).hexdigest(),
            }

        if method == "POST" and api_path.endswith("/git/blobs"):
            state["blob_number"] += 1
            blob_sha = f"blob-{state['blob_number']}"
            blobs[blob_sha] = base64.b64decode(payload["content"])
            return {"sha": blob_sha}

        if method == "POST" and api_path.endswith("/git/trees"):
            state["tree_number"] += 1
            tree_sha = f"tree-{state['tree_number']}"
            files = dict(tree_files[payload["base_tree"]])
            paths = set()
            for entry in payload["tree"]:
                paths.add(entry["path"])
                files[entry["path"]] = blobs[entry["sha"]]
            tree_path_sets.append(paths)
            tree_files[tree_sha] = files
            return {"sha": tree_sha}

        if method == "POST" and api_path.endswith("/git/commits"):
            state["commit_number"] += 1
            commit_sha = f"commit-{state['commit_number']}"
            commit_files[commit_sha] = dict(tree_files[payload["tree"]])
            commit_parents[commit_sha] = payload["parents"][0]
            head_trees[commit_sha] = payload["tree"]
            return {"sha": commit_sha}

        if method == "PATCH" and "/git/refs/heads/" in api_path:
            state["patch_attempts"] += 1
            visible_before_ref_updates.append(
                dict(snapshots[state["visible_head"]])
            )
            if state["patch_attempts"] == 1:
                concurrent_files = dict(initial_files)
                concurrent_files[server.ADMIN_CONFIG_REPO_PATH] = (
                    json.dumps(concurrent_config).encode("utf-8")
                )
                snapshots["head-2"] = concurrent_files
                tree_files["tree-head-2"] = dict(concurrent_files)
                head_trees["head-2"] = "tree-head-2"
                state["visible_head"] = "head-2"
                raise RuntimeError(
                    "GitHub API 422: Update is not a fast forward"
                )

            commit_sha = payload["sha"]
            assert commit_parents[commit_sha] == state["visible_head"]
            snapshots[commit_sha] = dict(commit_files[commit_sha])
            state["visible_head"] = commit_sha
            state["successful_ref_updates"] += 1
            return {"object": {"sha": commit_sha}}

        raise AssertionError(f"Unexpected GitHub request: {method} {url}")

    monkeypatch.setattr(server, "running_on_vercel", lambda: True)
    monkeypatch.setattr(server, "session_secret_configured", lambda: True)
    monkeypatch.setattr(server, "github_enabled", lambda: True)
    monkeypatch.setattr(server, "_github_request", fake_github_request)

    def update_logo(config):
        config["logo"] = new_logo
        return config

    def update_homepage(_config, reader):
        current = reader(server.HOMEPAGE_REPO_PATH).decode("utf-8")
        return {
            server.HOMEPAGE_REPO_PATH: server.apply_homepage_updates(
                current,
                {"logo": new_logo},
            )
        }

    updated = server.mutate_config_atomic(
        update_logo,
        publish_public=True,
        extra_changes_builder=update_homepage,
        message="test: atomic homepage settings",
    )

    final_files = snapshots[state["visible_head"]]
    final_config = json.loads(
        final_files[server.ADMIN_CONFIG_REPO_PATH].decode("utf-8")
    )
    final_public = json.loads(
        final_files[server.PUBLIC_CONFIG_REPO_PATH].decode("utf-8")
    )
    expected_paths = {
        server.ADMIN_CONFIG_REPO_PATH,
        server.PUBLIC_CONFIG_REPO_PATH,
        server.PUBLIC_RUNTIME_REPO_PATH,
        server.HOMEPAGE_REPO_PATH,
    }

    assert state["patch_attempts"] == 2
    assert state["successful_ref_updates"] == 1
    assert all(paths == expected_paths for paths in tree_path_sets)
    assert not any(method == "PUT" for method, _url, _payload in calls)
    assert all(
        snapshot[server.PUBLIC_CONFIG_REPO_PATH] == b"old-public-config"
        for snapshot in visible_before_ref_updates
    )
    assert updated["password_hash"] == "concurrent-password-hash"
    assert final_config["password_hash"] == "concurrent-password-hash"
    assert final_config["session_epoch"] == "concurrent-credential-version"
    assert final_config["logo"] == new_logo
    assert final_public["logo"] == new_logo
    assert new_logo.encode("utf-8") in final_files[server.PUBLIC_RUNTIME_REPO_PATH]
    assert new_logo.encode("utf-8") in final_files[server.HOMEPAGE_REPO_PATH]


def test_local_atomic_file_replace_rolls_back_partial_failure(
    tmp_path,
    monkeypatch,
):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("old-first", encoding="utf-8")
    second.write_text("old-second", encoding="utf-8")
    targets = {"first": first, "second": second}
    monkeypatch.setattr(
        server,
        "repository_path_to_local",
        lambda repo_path: targets[repo_path],
    )
    original_replace = Path.replace
    failed = False

    def fail_second_replace(path, target):
        nonlocal failed
        if not failed and Path(target) == second and path.suffix == ".tmp":
            failed = True
            raise OSError("simulated replace failure")
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", fail_second_replace)

    with pytest.raises(OSError, match="simulated replace failure"):
        server.write_repository_files_atomically(
            {
                "first": "new-first",
                "second": "new-second",
            }
        )

    assert first.read_text(encoding="utf-8") == "old-first"
    assert second.read_text(encoding="utf-8") == "old-second"
    assert list(tmp_path.glob(".*.tmp")) == []
    assert list(tmp_path.glob(".*.rollback")) == []


def test_production_secret_blocks_requests_and_allowed_material_is_stable(
    monkeypatch,
    client,
):
    for name in (
        "CMS_SECRET",
        "CMS_PASSWORD",
        "GITHUB_TOKEN",
        "VERCEL",
        "FLASK_ENV",
        "ENVIRONMENT",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CMS_ENV", "production")

    first_ephemeral = server.derive_session_secret()
    second_ephemeral = server.derive_session_secret()
    assert first_ephemeral != second_ephemeral
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.get_json()["session_secret_ready"] is False
    blocked = client.get("/api/me")
    assert blocked.status_code == 503
    assert blocked.get_json()["code"] == "MISSING_SESSION_SECRET"

    monkeypatch.setenv("CMS_PASSWORD", "a-strong-deployment-password")
    first = server.derive_session_secret()
    second = server.derive_session_secret()
    assert first == second
    assert len(first) == 32


def test_admin_and_api_responses_include_security_headers(client):
    for path in ("/admin", "/api/health"):
        response = client.get(path)
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "no-store" in response.headers["Cache-Control"]
        assert "frame-ancestors 'none'" in response.headers[
            "Content-Security-Policy"
        ]


def test_legacy_brand_media_names_are_filtered():
    assert server.legacy_media_filename("ADS-HTCON-900x603.png")
    assert server.legacy_media_filename("trung-tam-gia-su-binh-minh.png")
    assert not server.legacy_media_filename("feedback-tri-viet.png")
