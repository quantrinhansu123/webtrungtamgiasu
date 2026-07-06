let currentPageId = null;
let allPages = [];
let quill = null;
let mediaPickMode = null;
let inlineImageTarget = null;

const views = {
  pages: document.getElementById("view-pages"),
  editor: document.getElementById("view-editor"),
  media: document.getElementById("view-media"),
  settings: document.getElementById("view-settings"),
};

async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Có lỗi xảy ra");
  }
  return data;
}

function showView(name) {
  Object.entries(views).forEach(([key, el]) => {
    el.classList.toggle("hidden", key !== name);
  });
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === name);
  });
}

function setStatus(el, message, type = "") {
  el.textContent = message || "";
  el.className = `status ${type}`.trim();
}

function clearSelectedImage() {
  inlineImageTarget = null;
  document.getElementById("image-toolbar").classList.add("hidden");
  quill?.root.querySelectorAll("img.image-selected").forEach((img) => {
    img.classList.remove("image-selected");
  });
}

function selectInlineImage(img) {
  inlineImageTarget = img;
  quill.root.querySelectorAll("img.image-selected").forEach((node) => {
    node.classList.remove("image-selected");
  });
  img.classList.add("image-selected");
  document.getElementById("selected-image-preview").src = img.getAttribute("src") || "";
  document.getElementById("image-toolbar").classList.remove("hidden");
}

function insertImageAtCursor(url) {
  const range = quill.getSelection(true);
  const index = range ? range.index : quill.getLength();
  quill.insertEmbed(index, "image", url, "user");
  quill.setSelection(index + 1);
}

function applyInlineImage(url) {
  if (inlineImageTarget) {
    inlineImageTarget.setAttribute("src", url);
    document.getElementById("selected-image-preview").src = url;
    setStatus(document.getElementById("editor-status"), "Đã đổi ảnh trong bài", "success");
    return;
  }
  insertImageAtCursor(url);
  setStatus(document.getElementById("editor-status"), "Đã chèn ảnh vào bài", "success");
}

function initEditor() {
  if (quill) return;
  quill = new Quill("#editor-content", {
    theme: "snow",
    modules: {
      toolbar: {
        container: [
          [{ header: [1, 2, 3, false] }],
          ["bold", "italic", "underline", "strike"],
          [{ color: [] }, { background: [] }],
          [{ list: "ordered" }, { list: "bullet" }],
          [{ align: [] }],
          ["link", "image", "blockquote", "code-block"],
          ["clean"],
        ],
        handlers: {
          image: () => {
            inlineImageTarget = null;
            document.getElementById("inline-image-input").click();
          },
        },
      },
    },
  });

  quill.root.addEventListener("click", (event) => {
    if (event.target.tagName === "IMG") {
      selectInlineImage(event.target);
    }
  });
}

async function checkSession() {
  const me = await api("/api/me");
  if (me.logged_in) {
    document.getElementById("login-screen").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");
    initEditor();
    await loadPages();
    await loadSettings();
  }
}

async function login(event) {
  event.preventDefault();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  try {
    await api("/api/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    document.getElementById("login-screen").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");
    initEditor();
    await loadPages();
    await loadSettings();
  } catch (error) {
    setStatus(document.getElementById("login-status"), error.message, "error");
  }
}

async function logout() {
  await api("/api/logout", { method: "POST" });
  location.reload();
}

async function loadPages(search = "") {
  const status = document.getElementById("pages-status");
  setStatus(status, "Đang tải danh sách...");
  try {
    const query = search ? `?search=${encodeURIComponent(search)}` : "";
    const data = await api(`/api/pages${query}`);
    allPages = data.pages;
    renderPageList();
    setStatus(status, `Tổng cộng ${data.total} trang`, "success");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

function renderPageList() {
  const list = document.getElementById("page-list");
  if (!allPages.length) {
    list.innerHTML = "<p>Không có trang nào.</p>";
    return;
  }
  list.innerHTML = allPages
    .map(
      (page) => `
      <div class="page-item" data-id="${page.id}">
        <div>
          <strong>${escapeHtml(page.title)}</strong>
          <small>${escapeHtml(page.slug)}</small>
        </div>
        <span class="badge">${page.editable_content ? "Có nội dung" : "Trang tĩnh"}</span>
      </div>`
    )
    .join("");

  list.querySelectorAll(".page-item").forEach((item) => {
    item.addEventListener("click", () => openEditor(item.dataset.id));
  });
}

async function openEditor(pageId) {
  currentPageId = pageId;
  clearSelectedImage();
  const status = document.getElementById("editor-status");
  setStatus(status, "Đang tải bài viết...");
  try {
    const page = await api(`/api/pages/${pageId}`);
    document.getElementById("editor-title").textContent = page.title || "Chỉnh sửa bài viết";
    document.getElementById("field-title").value = page.title || "";
    document.getElementById("field-heading").value = page.heading || "";
    document.getElementById("field-description").value = page.description || "";
    document.getElementById("field-thumbnail").value = page.thumbnail || "";
    document.getElementById("thumbnail-preview").src = normalizeAssetUrl(page.thumbnail);
    document.getElementById("preview-link").href = page.public_url;
    quill.root.innerHTML = page.content || "<p></p>";
    showView("editor");
    setStatus(status, "");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

async function savePage() {
  if (!currentPageId) return;
  const status = document.getElementById("editor-status");
  setStatus(status, "Đang lưu...");
  try {
    await api(`/api/pages/${currentPageId}`, {
      method: "PUT",
      body: JSON.stringify({
        title: document.getElementById("field-title").value.trim(),
        heading: document.getElementById("field-heading").value.trim(),
        description: document.getElementById("field-description").value.trim(),
        thumbnail: document.getElementById("field-thumbnail").value.trim(),
        content: quill.root.innerHTML,
      }),
    });
    setStatus(status, "Đã lưu bài viết thành công", "success");
    await loadPages(document.getElementById("page-search").value.trim());
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

async function loadMedia(search = "") {
  const status = document.getElementById("media-status");
  setStatus(status, "Đang tải ảnh...");
  try {
    const query = search ? `?search=${encodeURIComponent(search)}` : "";
    const data = await api(`/api/media${query}`);
    renderMedia(data.media);
    setStatus(status, `${data.media.length} ảnh`, "success");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

function handleMediaPick(item) {
  if (mediaPickMode === "thumbnail") {
    document.getElementById("field-thumbnail").value = item.path;
    document.getElementById("thumbnail-preview").src = item.url;
    mediaPickMode = null;
    showView("editor");
    return;
  }

  if (mediaPickMode === "inline") {
    applyInlineImage(item.url);
    mediaPickMode = null;
    showView("editor");
    return;
  }

  navigator.clipboard.writeText(item.url).catch(() => {});
  setStatus(document.getElementById("media-status"), `Đã chọn: ${item.path}`, "success");
}

function renderMedia(items) {
  const grid = document.getElementById("media-grid");
  if (!items.length) {
    grid.innerHTML = "<p>Chưa có ảnh.</p>";
    return;
  }
  grid.innerHTML = items
    .map(
      (item) => `
      <div class="media-card" data-url="${escapeAttr(item.url)}" data-path="${escapeAttr(item.path)}">
        <img src="${escapeAttr(item.url)}" alt="${escapeAttr(item.name)}" loading="lazy" />
        <p>${escapeHtml(item.name)}</p>
      </div>`
    )
    .join("");

  grid.querySelectorAll(".media-card").forEach((card) => {
    card.addEventListener("click", () => {
      handleMediaPick({
        url: card.dataset.url,
        path: card.dataset.path,
      });
    });
  });
}

async function uploadFile(file, onDone) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("/api/media/upload", {
    method: "POST",
    credentials: "same-origin",
    body: formData,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Upload thất bại");
  }
  onDone(data);
}

async function loadSettings() {
  const data = await api("/api/settings");
  document.getElementById("setting-site-name").value = data.site_name || "";
  document.getElementById("setting-logo").value = data.logo || "";
  document.getElementById("setting-hotline1").value = data.hotline1 || "";
  document.getElementById("setting-hotline2").value = data.hotline2 || "";
  document.getElementById("setting-logo-preview").src = normalizeAssetUrl(data.logo);
}

async function saveSettings() {
  const status = document.getElementById("settings-status");
  setStatus(status, "Đang lưu...");
  try {
    const payload = {
      site_name: document.getElementById("setting-site-name").value.trim(),
      logo: document.getElementById("setting-logo").value.trim(),
      hotline1: document.getElementById("setting-hotline1").value.trim(),
      hotline2: document.getElementById("setting-hotline2").value.trim(),
    };
    const newPassword = document.getElementById("setting-password").value;
    if (newPassword) payload.new_password = newPassword;
    await api("/api/settings", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    setStatus(status, "Đã cập nhật cài đặt", "success");
    document.getElementById("setting-password").value = "";
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

function normalizeAssetUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  if (path.startsWith("/")) return path;
  return `/giasubinhminh.com/${path.replace(/^\.?\//, "")}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("'", "&#39;");
}

document.getElementById("login-form").addEventListener("submit", login);
document.getElementById("logout-btn").addEventListener("click", logout);
document.getElementById("save-page").addEventListener("click", savePage);
document.getElementById("save-settings").addEventListener("click", saveSettings);
document.getElementById("back-to-list").addEventListener("click", () => {
  clearSelectedImage();
  showView("pages");
});
document.getElementById("close-image-toolbar").addEventListener("click", clearSelectedImage);

document.getElementById("page-search").addEventListener("input", (event) => {
  loadPages(event.target.value.trim());
});

document.getElementById("media-search").addEventListener("input", (event) => {
  loadMedia(event.target.value.trim());
});

document.getElementById("field-thumbnail").addEventListener("input", (event) => {
  document.getElementById("thumbnail-preview").src = normalizeAssetUrl(event.target.value.trim());
});

document.getElementById("setting-logo").addEventListener("input", (event) => {
  document.getElementById("setting-logo-preview").src = normalizeAssetUrl(event.target.value.trim());
});

document.getElementById("pick-thumbnail").addEventListener("click", async () => {
  mediaPickMode = "thumbnail";
  showView("media");
  await loadMedia();
});

document.getElementById("replace-image-library").addEventListener("click", async () => {
  mediaPickMode = "inline";
  showView("media");
  await loadMedia();
});

document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const view = btn.dataset.view;
    if (view === "pages") showView("pages");
    if (view === "media") {
      mediaPickMode = null;
      showView("media");
      await loadMedia();
    }
    if (view === "settings") {
      showView("settings");
      await loadSettings();
    }
  });
});

document.getElementById("upload-media").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const status = document.getElementById("media-status");
  try {
    setStatus(status, "Đang tải lên...");
    await uploadFile(file, async () => {
      await loadMedia(document.getElementById("media-search").value.trim());
      setStatus(status, "Tải ảnh thành công", "success");
    });
  } catch (error) {
    setStatus(status, error.message, "error");
  } finally {
    event.target.value = "";
  }
});

document.getElementById("upload-thumbnail").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const status = document.getElementById("editor-status");
  try {
    setStatus(status, "Đang tải ảnh...");
    await uploadFile(file, (data) => {
      document.getElementById("field-thumbnail").value = data.path;
      document.getElementById("thumbnail-preview").src = data.url;
      setStatus(status, "Đã tải ảnh đại diện", "success");
    });
  } catch (error) {
    setStatus(status, error.message, "error");
  } finally {
    event.target.value = "";
  }
});

document.getElementById("inline-image-input").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const status = document.getElementById("editor-status");
  try {
    setStatus(status, "Đang tải ảnh...");
    await uploadFile(file, (data) => {
      applyInlineImage(data.url);
    });
  } catch (error) {
    setStatus(status, error.message, "error");
  } finally {
    event.target.value = "";
  }
});

checkSession().catch(() => {});
