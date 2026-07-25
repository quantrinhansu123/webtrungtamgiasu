let currentPageId = null;
let allPages = [];
let quill = null;
let mediaPickMode = null;
let inlineImageTarget = null;
let currentClassId = null;
let allClasses = [];

const FEATURED_CAM_KET_ID = "cam-ket-tien-bo-sau-10-buoi/index.html";
const CMS_USERNAME_KEY = "tri_viet_cms_username";
const CMS_PASSWORD_KEY = "tri_viet_cms_password";

function getCmsCredentials() {
  return {
    username: sessionStorage.getItem(CMS_USERNAME_KEY) || "",
    password: sessionStorage.getItem(CMS_PASSWORD_KEY) || "",
  };
}

function setCmsCredentials(username, password) {
  if (username && password) {
    sessionStorage.setItem(CMS_USERNAME_KEY, username);
    sessionStorage.setItem(CMS_PASSWORD_KEY, password);
    return;
  }
  sessionStorage.removeItem(CMS_USERNAME_KEY);
  sessionStorage.removeItem(CMS_PASSWORD_KEY);
}

function cmsAuthHeaders() {
  const credentials = getCmsCredentials();
  if (!credentials.username || !credentials.password) return {};
  return {
    "X-CMS-Username": credentials.username,
    "X-CMS-Password": credentials.password,
  };
}

const views = {
  pages: document.getElementById("view-pages"),
  homepage: document.getElementById("view-homepage"),
  feedback: document.getElementById("view-feedback"),
  classes: document.getElementById("view-classes"),
  editor: document.getElementById("view-editor"),
  media: document.getElementById("view-media"),
  settings: document.getElementById("view-settings"),
};

function setActiveNav(viewName, pageId = null) {
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    const isFeatured =
      btn.dataset.view === "featured-cam-ket" &&
      pageId === FEATURED_CAM_KET_ID &&
      viewName === "editor";
    const isMatch = btn.dataset.view === viewName;
    btn.classList.toggle("active", isFeatured || (isMatch && viewName !== "editor"));
  });
}

async function api(url, options = {}) {
  const optionHeaders = options.headers || {};
  const response = await fetch(url, {
    credentials: "same-origin",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...cmsAuthHeaders(),
      ...optionHeaders,
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Có lỗi xảy ra");
  }
  return data;
}

function showView(name) {
  Object.entries(views).forEach(([key, el]) => {
    if (!el) return;
    el.classList.toggle("hidden", key !== name);
  });
  if (name === "editor" && currentPageId === FEATURED_CAM_KET_ID) {
    setActiveNav("editor", FEATURED_CAM_KET_ID);
  } else {
    setActiveNav(name);
  }
}

function setStatus(el, message, type = "") {
  el.textContent = message || "";
  el.className = `status ${type}`.trim();
}

function clearSelectedImage() {
  inlineImageTarget = null;
  document.getElementById("image-toolbar").classList.add("hidden");
  document.getElementById("inline-image-url").value = "";
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
  document.getElementById("inline-image-url").value = img.getAttribute("src") || "";
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

async function enterAdmin() {
  document.getElementById("login-screen").classList.add("hidden");
  document.getElementById("app").classList.remove("hidden");
  initEditor();
  await loadPages();
  await loadSettings();
  await openFromHash();
}

async function checkSession() {
  const me = await api("/api/me");
  if (me.logged_in) {
    await enterAdmin();
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
    setCmsCredentials(username, password);
    await enterAdmin();
  } catch (error) {
    setCmsCredentials("", "");
    setStatus(document.getElementById("login-status"), error.message, "error");
  }
}

async function logout() {
  try {
    await api("/api/logout", { method: "POST" });
  } finally {
    setCmsCredentials("", "");
  }
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
    document.getElementById("editor-title").textContent =
      pageId === FEATURED_CAM_KET_ID
        ? "Quản trị: Cam kết tiến bộ sau 10 buổi"
        : page.title || "Chỉnh sửa bài viết";
    document.getElementById("field-title").value = page.title || "";
    document.getElementById("field-heading").value = page.heading || "";
    document.getElementById("field-description").value = page.description || "";
    document.getElementById("field-thumbnail").value = page.thumbnail || "";
    document.getElementById("thumbnail-preview").src = normalizeAssetUrl(page.thumbnail);
    document.getElementById("field-rating-score").value =
      page.rating_score === null || page.rating_score === undefined ? "" : page.rating_score;
    document.getElementById("field-rating-count").value =
      page.rating_count === null || page.rating_count === undefined ? "" : page.rating_count;
    renderRatingPreview();
    document.getElementById("preview-link").href = page.public_url;
    quill.root.innerHTML = page.content || "<p></p>";
    showView("editor");
    if (pageId === FEATURED_CAM_KET_ID) {
      history.replaceState(null, "", "#cam-ket-tien-bo-sau-10-buoi");
    }
    setStatus(status, "");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

async function openFeaturedCamKet() {
  await openEditor(FEATURED_CAM_KET_ID);
}

function renderWhyFeatures(features = []) {
  const wrap = document.getElementById("home-why-features");
  wrap.innerHTML = Array.from({ length: 4 }, (_, i) => {
    const item = features[i] || { title: "", text: "" };
    return `
      <div class="home-feature-card">
        <div class="field">
          <label>Ô ${i + 1} — tiêu đề</label>
          <input class="home-why-feature-title" type="text" value="${escapeAttr(item.title || "")}" />
        </div>
        <div class="field" style="margin-bottom:0">
          <label>Ô ${i + 1} — nội dung</label>
          <textarea class="home-why-feature-text">${escapeHtml(item.text || "")}</textarea>
        </div>
      </div>`;
  }).join("");
}

function formatSizeLabel(width, height, fallback = "Chưa có ảnh") {
  if (width && height) return `${width} × ${height} px`;
  return fallback;
}

function bindPreviewSize(img, badgeEl, recommendedText = "") {
  const update = () => {
    if (!img.naturalWidth) {
      badgeEl.textContent = "Khổ ảnh: Chưa có ảnh";
      return;
    }
    badgeEl.textContent = `Khổ ảnh: ${formatSizeLabel(img.naturalWidth, img.naturalHeight)}`;
  };
  img.addEventListener("load", update);
  img.addEventListener("error", () => {
    badgeEl.textContent = "Khổ ảnh: Không tải được";
  });
  if (img.complete) update();
  if (recommendedText) {
    const hint = badgeEl.parentElement?.querySelector(".size-hint");
    if (hint) hint.textContent = recommendedText;
  }
}

function renderSlides(slides = []) {
  const wrap = document.getElementById("home-slides");
  wrap.innerHTML = Array.from({ length: 3 }, (_, i) => {
    const item = slides[i] || { id: "", image: "", size_label: "" };
    const preview = normalizeAssetUrl(item.image || "");
    const sizeLabel = item.size_label || formatSizeLabel(item.width, item.height);
    return `
      <div class="home-slide-card" data-slide-id="${escapeAttr(item.id || "")}">
        <div class="field" style="margin-bottom:0">
          <label>Ảnh slide ${i + 1}</label>
          <div class="home-media-row">
            <input class="home-slide-image" type="text" value="${escapeAttr(item.image || "")}" />
            <label class="btn btn-secondary" for="upload-home-slide-${i}">Tải ảnh</label>
            <input id="upload-home-slide-${i}" class="home-slide-upload hidden" type="file" accept="image/*" data-index="${i}" />
          </div>
          <div class="home-size-meta">
            <span class="size-badge home-slide-size">Khổ ảnh: ${escapeHtml(sizeLabel || "—")}</span>
            <span class="size-hint">Khổ chuẩn slide: 1360 × 540 px</span>
          </div>
          <div class="home-preview-frame home-preview-frame-slide">
            <img class="home-slide-preview" src="${escapeAttr(preview)}" alt="Slide ${i + 1}" />
          </div>
        </div>
      </div>`;
  }).join("");

  wrap.querySelectorAll(".home-slide-card").forEach((card) => {
    const input = card.querySelector(".home-slide-image");
    const preview = card.querySelector(".home-slide-preview");
    const badge = card.querySelector(".home-slide-size");
    bindPreviewSize(preview, badge, "Khổ chuẩn slide: 1360 × 540 px");
    input.addEventListener("input", () => {
      preview.src = normalizeAssetUrl(input.value.trim());
    });
  });

  wrap.querySelectorAll(".home-slide-upload").forEach((input) => {
    input.addEventListener("change", async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      const card = event.target.closest(".home-slide-card");
      const status = document.getElementById("homepage-status");
      try {
        setStatus(status, "Đang tải ảnh slide...");
        await uploadFile(file, async (data) => {
          const field = card.querySelector(".home-slide-image");
          const preview = card.querySelector(".home-slide-preview");
          const badge = card.querySelector(".home-slide-size");
          field.value = data.path;
          preview.src = data.url;
          badge.textContent = `Khổ ảnh: ${data.size_label || formatSizeLabel(data.width, data.height)}`;
          setStatus(status, "Đã tải ảnh — đang lưu vào slide...", "success");
          await saveHomepage();
        });
      } catch (error) {
        setStatus(status, error.message, "error");
      } finally {
        event.target.value = "";
      }
    });
  });
}

function renderCommitItems(items = []) {
  const wrap = document.getElementById("home-commit-items");
  wrap.innerHTML = Array.from({ length: 7 }, (_, i) => {
    const value = items[i] || "";
    return `
      <div class="field" style="margin-bottom:0">
        <label>Cam kết ${i + 1}</label>
        <input class="home-commit-item" type="text" value="${escapeAttr(value)}" />
      </div>`;
  }).join("");
}

function renderTutors(tutors = []) {
  const wrap = document.getElementById("home-tutors");
  wrap.innerHTML = Array.from({ length: 4 }, (_, i) => {
    const item = tutors[i] || { title: "", text: "", image: "" };
    return `
      <div class="home-tutor-card">
        <div class="field">
          <label>Gia sư ${i + 1} — môn / vai trò</label>
          <input class="home-tutor-title" type="text" value="${escapeAttr(item.title || "")}" />
        </div>
        <div class="field">
          <label>Mô tả</label>
          <textarea class="home-tutor-text">${escapeHtml(item.text || "")}</textarea>
        </div>
        <div class="field" style="margin-bottom:0">
          <label>Ảnh (URL)</label>
          <input class="home-tutor-image" type="text" value="${escapeAttr(item.image || "")}" />
        </div>
      </div>`;
  }).join("");
}

async function loadHomepage() {
  const status = document.getElementById("homepage-status");
  setStatus(status, "Đang tải trang chủ...");
  try {
    const data = await api("/api/homepage");
    document.getElementById("home-title").value = data.title || "";
    document.getElementById("home-description").value = data.description || "";
    document.getElementById("home-logo").value = data.logo || "";
    document.getElementById("home-logo-preview").src = normalizeAssetUrl(data.logo || "");
    document.getElementById("home-logo-size").textContent =
      `Khổ ảnh: ${data.logo_size_label || formatSizeLabel(data.logo_width, data.logo_height)}`;
    bindPreviewSize(
      document.getElementById("home-logo-preview"),
      document.getElementById("home-logo-size"),
      "Gợi ý logo: 186 × 100 px"
    );
    renderSlides(data.slides || []);
    document.getElementById("home-why-title").value = data.why_title || "";
    document.getElementById("home-why-subtitle").value = data.why_subtitle || "";
    renderWhyFeatures(data.why_features || []);
    document.getElementById("home-subjects-title").value = data.subjects_title || "";
    document.getElementById("home-subjects-intro").value = data.subjects_intro || "";
    document.getElementById("home-commit-title").value = data.commit_title || "";
    document.getElementById("home-commit-image").value = data.commit_image || "";
    renderCommitItems(data.commit_items || []);
    document.getElementById("home-banner-title").value = data.banner_title || "";
    document.getElementById("home-banner-subtitle").value = data.banner_subtitle || "";
    document.getElementById("home-banner-cta").value = data.banner_cta || "";
    document.getElementById("home-banner-phone").value = data.banner_phone || "";
    document.getElementById("home-team-title").value = data.team_title || "";
    document.getElementById("home-teacher-title").value = data.teacher_title || "";
    document.getElementById("home-teacher-html").value = data.teacher_html || "";
    document.getElementById("home-student-title").value = data.student_title || "";
    document.getElementById("home-student-html").value = data.student_html || "";
    document.getElementById("home-register-label").value = data.register_label || "";
    document.getElementById("home-tutors-title").value = data.tutors_title || "";
    renderTutors(data.tutors || []);
    setStatus(status, "Đã tải nội dung trang chủ", "success");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

async function openHomepage() {
  history.replaceState(null, "", "#trang-chu");
  showView("homepage");
  await loadHomepage();
}

async function saveHomepage() {
  const status = document.getElementById("homepage-status");
  setStatus(status, "Đang lưu...");
  const whyFeatures = Array.from(document.querySelectorAll(".home-feature-card")).map((card) => ({
    title: card.querySelector(".home-why-feature-title").value.trim(),
    text: card.querySelector(".home-why-feature-text").value.trim(),
  }));
  const slides = Array.from(document.querySelectorAll(".home-slide-card")).map((card) => ({
    id: card.dataset.slideId || "",
    image: normalizeAssetUrl(card.querySelector(".home-slide-image").value.trim()),
  }));
  const commitItems = Array.from(document.querySelectorAll(".home-commit-item")).map((input) =>
    input.value.trim()
  );
  const tutors = Array.from(document.querySelectorAll(".home-tutor-card")).map((card) => ({
    title: card.querySelector(".home-tutor-title").value.trim(),
    text: card.querySelector(".home-tutor-text").value.trim(),
    image: normalizeAssetUrl(card.querySelector(".home-tutor-image").value.trim()),
  }));

  try {
    await api("/api/homepage", {
      method: "PUT",
      body: JSON.stringify({
        title: document.getElementById("home-title").value.trim(),
        description: document.getElementById("home-description").value.trim(),
        logo: normalizeAssetUrl(document.getElementById("home-logo").value.trim()),
        slides,
        why_title: document.getElementById("home-why-title").value.trim(),
        why_subtitle: document.getElementById("home-why-subtitle").value.trim(),
        why_features: whyFeatures,
        subjects_title: document.getElementById("home-subjects-title").value.trim(),
        subjects_intro: document.getElementById("home-subjects-intro").value.trim(),
        commit_title: document.getElementById("home-commit-title").value.trim(),
        commit_image: normalizeAssetUrl(document.getElementById("home-commit-image").value.trim()),
        commit_items: commitItems,
        banner_title: document.getElementById("home-banner-title").value.trim(),
        banner_subtitle: document.getElementById("home-banner-subtitle").value.trim(),
        banner_cta: document.getElementById("home-banner-cta").value.trim(),
        banner_phone: document.getElementById("home-banner-phone").value.trim(),
        team_title: document.getElementById("home-team-title").value.trim(),
        teacher_title: document.getElementById("home-teacher-title").value.trim(),
        teacher_html: document.getElementById("home-teacher-html").value,
        student_title: document.getElementById("home-student-title").value.trim(),
        student_html: document.getElementById("home-student-html").value,
        register_label: document.getElementById("home-register-label").value.trim(),
        tutors_title: document.getElementById("home-tutors-title").value.trim(),
        tutors,
      }),
    });
    setStatus(status, "Đã lưu trang chủ thành công", "success");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

function localDateValue(date = new Date()) {
  const offset = date.getTimezoneOffset();
  return new Date(date.getTime() - offset * 60000).toISOString().slice(0, 10);
}

function resetClassForm() {
  currentClassId = null;
  document.getElementById("class-id").value = "";
  document.getElementById("class-title").value = `LỚP MỚI NGÀY ${new Intl.DateTimeFormat("vi-VN").format(new Date())}`;
  document.getElementById("class-date").value = localDateValue();
  document.getElementById("class-content").value = "";
  document.getElementById("class-form-title").textContent = "Tạo bài lớp mới";
  document.getElementById("save-class").textContent = "Đăng lớp mới";
  document.getElementById("cancel-class-edit").classList.add("hidden");
}

function renderClasses() {
  const list = document.getElementById("class-admin-list");
  if (!allClasses.length) {
    list.innerHTML = "<p>Chưa có bài lớp mới.</p>";
    return;
  }
  list.innerHTML = allClasses.map((item) => {
    const excerpt = String(item.content || "").replaceAll("\n", " ").slice(0, 150);
    return `
      <article class="class-admin-item" data-id="${escapeAttr(item.id)}">
        <div>
          <small>${escapeHtml(item.date || "")}</small>
          <strong>${escapeHtml(item.title || "")}</strong>
          <p>${escapeHtml(excerpt)}${String(item.content || "").length > 150 ? "..." : ""}</p>
        </div>
        <div class="class-admin-actions">
          <button class="btn btn-secondary edit-class" type="button">Chỉnh sửa</button>
          <button class="btn btn-danger delete-class" type="button">Xóa</button>
        </div>
      </article>`;
  }).join("");

  list.querySelectorAll(".edit-class").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.closest(".class-admin-item").dataset.id;
      const item = allClasses.find((entry) => entry.id === id);
      if (!item) return;
      currentClassId = item.id;
      document.getElementById("class-id").value = item.id;
      document.getElementById("class-title").value = item.title || "";
      document.getElementById("class-date").value = item.date || localDateValue();
      document.getElementById("class-content").value = item.content || "";
      document.getElementById("class-form-title").textContent = "Chỉnh sửa bài lớp mới";
      document.getElementById("save-class").textContent = "Lưu thay đổi";
      document.getElementById("cancel-class-edit").classList.remove("hidden");
      document.getElementById("class-title").focus();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });

  list.querySelectorAll(".delete-class").forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.closest(".class-admin-item").dataset.id;
      const item = allClasses.find((entry) => entry.id === id);
      if (!item || !window.confirm(`Xóa bài “${item.title}”?`)) return;
      const status = document.getElementById("classes-status");
      try {
        setStatus(status, "Đang xóa...");
        await api(`/api/classes/${id}`, { method: "DELETE" });
        if (currentClassId === id) resetClassForm();
        await loadClasses();
        setStatus(status, "Đã xóa bài lớp mới", "success");
      } catch (error) {
        setStatus(status, error.message, "error");
      }
    });
  });
}

async function loadClasses() {
  const status = document.getElementById("classes-status");
  setStatus(status, "Đang tải danh sách...");
  try {
    const data = await api("/api/classes");
    allClasses = data.classes || [];
    renderClasses();
    setStatus(status, `Đã tải ${data.total || 0} bài lớp mới`, "success");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

function renderFeedbackImages(images = []) {
  const wrap = document.getElementById("feedback-images");
  wrap.innerHTML = Array.from({ length: 6 }, (_, index) => {
    const item = images[index] || {};
    return `
      <div class="feedback-admin-card" data-index="${index}">
        <h3>Ảnh phản hồi ${index + 1}</h3>
        <img
          class="feedback-admin-preview"
          src="${escapeAttr(normalizeAssetUrl(item.url || ""))}"
          alt="Xem trước phản hồi ${index + 1}"
        />
        <div class="field">
          <label>Đường dẫn ảnh</label>
          <input
            class="feedback-image-url"
            type="text"
            value="${escapeAttr(item.url || "")}"
          />
          <p class="field-hint">Có thể dán link chia sẻ Google Drive.</p>
        </div>
        <div class="image-toolbar-actions">
          <button class="btn btn-primary normalize-feedback-url" type="button">Kiểm tra link</button>
          <label class="btn btn-secondary" for="upload-feedback-${index}">Tải ảnh mới</label>
        </div>
        <input
          id="upload-feedback-${index}"
          class="feedback-image-upload hidden"
          type="file"
          accept="image/*"
        />
      </div>`;
  }).join("");

  wrap.querySelectorAll(".feedback-admin-card").forEach((card) => {
    const urlInput = card.querySelector(".feedback-image-url");
    const preview = card.querySelector(".feedback-admin-preview");
    urlInput.addEventListener("input", () => {
      preview.src = normalizeAssetUrl(urlInput.value.trim());
    });
    card.querySelector(".normalize-feedback-url").addEventListener("click", () => {
      const normalized = normalizeAssetUrl(urlInput.value.trim());
      urlInput.value = normalized;
      preview.src = normalized;
      setStatus(
        document.getElementById("feedback-status"),
        normalized ? "Link ảnh hợp lệ. Bấm “Lưu phản hồi” để cập nhật." : "Chưa có đường dẫn ảnh.",
        normalized ? "success" : "error"
      );
    });
  });

  wrap.querySelectorAll(".feedback-image-upload").forEach((input) => {
    input.addEventListener("change", async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      const card = event.target.closest(".feedback-admin-card");
      const status = document.getElementById("feedback-status");
      try {
        setStatus(status, "Đang tải ảnh phản hồi...");
        await uploadFile(file, (data) => {
          card.querySelector(".feedback-image-url").value = data.url;
          card.querySelector(".feedback-admin-preview").src = data.url;
          setStatus(
            status,
            "Đã tải ảnh. Bấm “Lưu phản hồi” để cập nhật trang.",
            "success"
          );
        });
      } catch (error) {
        setStatus(status, error.message, "error");
      } finally {
        event.target.value = "";
      }
    });
  });
}

async function openFeedback() {
  const status = document.getElementById("feedback-status");
  showView("feedback");
  setStatus(status, "Đang tải phản hồi...");
  try {
    const data = await api("/api/feedback");
    renderFeedbackImages(data.images || []);
    setStatus(status, "");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

async function saveFeedback() {
  const status = document.getElementById("feedback-status");
  const images = Array.from(
    document.querySelectorAll(".feedback-admin-card")
  ).map((card) => ({
    url: normalizeAssetUrl(card.querySelector(".feedback-image-url").value.trim()),
  }));
  setStatus(status, "Đang lưu phản hồi...");
  try {
    const data = await api("/api/feedback", {
      method: "PUT",
      body: JSON.stringify({
        images,
      }),
    });
    setStatus(status, data.message || "Đã lưu phản hồi", "success");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

async function openClasses() {
  history.replaceState(null, "", "#dang-lop-moi");
  showView("classes");
  if (!document.getElementById("class-date").value) resetClassForm();
  await loadClasses();
}

async function saveClass() {
  const status = document.getElementById("classes-status");
  const isEditing = Boolean(currentClassId);
  const payload = {
    title: document.getElementById("class-title").value.trim(),
    date: document.getElementById("class-date").value,
    content: document.getElementById("class-content").value.trim(),
  };
  try {
    setStatus(status, isEditing ? "Đang lưu thay đổi..." : "Đang đăng lớp mới...");
    await api(isEditing ? `/api/classes/${currentClassId}` : "/api/classes", {
      method: isEditing ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    resetClassForm();
    await loadClasses();
    setStatus(status, isEditing ? "Đã cập nhật lớp mới" : "Đã đăng lớp mới", "success");
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

async function openFromHash() {
  const hash = (location.hash || "").replace(/^#/, "");
  if (hash === "cam-ket-tien-bo-sau-10-buoi" || hash === "featured-cam-ket") {
    await openFeaturedCamKet();
  } else if (hash === "trang-chu" || hash === "homepage") {
    await openHomepage();
  } else if (hash === "dang-lop-moi" || hash === "lop-moi") {
    await openClasses();
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
        thumbnail: normalizeAssetUrl(document.getElementById("field-thumbnail").value.trim()),
        rating_score: document.getElementById("field-rating-score").value,
        rating_count: document.getElementById("field-rating-count").value,
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
    headers: cmsAuthHeaders(),
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
  document
    .getElementById("cms-publishing-warning")
    .classList.toggle("hidden", data.publishing_ready !== false);
}

async function saveSettings() {
  const status = document.getElementById("settings-status");
  setStatus(status, "Đang lưu...");
  try {
    const payload = {
      site_name: document.getElementById("setting-site-name").value.trim(),
      logo: normalizeAssetUrl(document.getElementById("setting-logo").value.trim()),
      hotline1: document.getElementById("setting-hotline1").value.trim(),
      hotline2: document.getElementById("setting-hotline2").value.trim(),
    };
    const newPassword = document.getElementById("setting-password").value;
    if (newPassword) payload.new_password = newPassword;
    await api("/api/settings", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    if (newPassword) {
      const credentials = getCmsCredentials();
      setCmsCredentials(credentials.username || "admin", newPassword);
    }
    setStatus(status, "Đã cập nhật cài đặt", "success");
    document.getElementById("setting-password").value = "";
  } catch (error) {
    setStatus(status, error.message, "error");
  }
}

function googleDriveFileId(value) {
  const pathMatch = String(value || "").match(/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)/i);
  if (pathMatch) return pathMatch[1];
  try {
    const url = new URL(String(value || ""));
    if (/drive\.google\.com$/i.test(url.hostname)) {
      return url.searchParams.get("id") || "";
    }
  } catch (_) {
    return "";
  }
  return "";
}

function normalizeAssetUrl(path) {
  const value = String(path || "").trim();
  if (!value) return "";
  const driveId = googleDriveFileId(value);
  if (driveId) return `https://drive.google.com/thumbnail?id=${driveId}&sz=w2000`;
  if (value.startsWith("http")) return value;
  if (value.startsWith("/")) return value;
  const cleaned = value.replace(/^(?:\.\.\/)+/, "").replace(/^\.?\//, "");
  if (cleaned.startsWith("giasubinhminh.com/")) return `/${cleaned}`;
  return `/giasubinhminh.com/${cleaned}`;
}

function renderRatingPreview() {
  const scoreInput = document.getElementById("field-rating-score");
  const countInput = document.getElementById("field-rating-count");
  const target = document.getElementById("rating-live-preview");
  if (!scoreInput || !countInput || !target) return;
  const rawScore = Number(scoreInput.value);
  const score = Number.isFinite(rawScore) ? Math.min(5, Math.max(0, rawScore)) : 0;
  const count = Math.max(0, Number.parseInt(countInput.value || "0", 10) || 0);
  const filled = Math.round(score);
  target.innerHTML =
    `${"★".repeat(filled)}<span style="color:#d6d6d6">${"☆".repeat(5 - filled)}</span>` +
    `<small>${score.toFixed(1)}/5 — ${count} bình chọn</small>`;
}

function previewDriveImage() {
  const source = document.getElementById("drive-image-url").value.trim();
  const normalized = normalizeAssetUrl(source);
  const status = document.getElementById("drive-status");
  if (!source || !googleDriveFileId(source)) {
    document.getElementById("drive-preview-wrap").classList.add("hidden");
    setStatus(status, "Link chưa đúng định dạng Google Drive.", "error");
    return;
  }
  const preview = document.getElementById("drive-image-preview");
  document.getElementById("drive-normalized-url").value = normalized;
  preview.src = normalized;
  preview.onload = () => {
    document.getElementById("drive-preview-wrap").classList.remove("hidden");
    setStatus(status, "Ảnh đã tải được. Có thể sao chép đường dẫn để dùng.", "success");
  };
  preview.onerror = () => {
    document.getElementById("drive-preview-wrap").classList.remove("hidden");
    setStatus(
      status,
      "Không xem được ảnh. Hãy bật quyền “Bất kỳ ai có liên kết — Người xem” trong Drive.",
      "error"
    );
  };
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
document.getElementById("save-homepage").addEventListener("click", saveHomepage);
document.getElementById("save-feedback").addEventListener("click", saveFeedback);
document.getElementById("save-class").addEventListener("click", saveClass);
document.getElementById("new-class").addEventListener("click", resetClassForm);
document.getElementById("cancel-class-edit").addEventListener("click", resetClassForm);
document.getElementById("back-to-list").addEventListener("click", () => {
  clearSelectedImage();
  history.replaceState(null, "", " ");
  showView("pages");
});
document.getElementById("close-image-toolbar").addEventListener("click", clearSelectedImage);
document.getElementById("open-featured-cam-ket").addEventListener("click", openFeaturedCamKet);
document.getElementById("open-homepage").addEventListener("click", openHomepage);
document.getElementById("field-rating-score").addEventListener("input", renderRatingPreview);
document.getElementById("field-rating-count").addEventListener("input", renderRatingPreview);

document.querySelectorAll("[data-quick-view]").forEach((button) => {
  button.addEventListener("click", async () => {
    const view = button.dataset.quickView;
    if (view === "homepage") await openHomepage();
    if (view === "feedback") await openFeedback();
    if (view === "classes") await openClasses();
    if (view === "media") {
      mediaPickMode = null;
      showView("media");
      await loadMedia();
    }
  });
});

document.getElementById("apply-inline-image-url").addEventListener("click", () => {
  const field = document.getElementById("inline-image-url");
  const url = normalizeAssetUrl(field.value.trim());
  if (!url) {
    setStatus(document.getElementById("editor-status"), "Chưa có đường dẫn ảnh.", "error");
    return;
  }
  field.value = url;
  applyInlineImage(url);
});

document.getElementById("preview-drive-image").addEventListener("click", previewDriveImage);
document.getElementById("drive-image-url").addEventListener("keydown", (event) => {
  if (event.key === "Enter") previewDriveImage();
});
document.getElementById("copy-drive-image-url").addEventListener("click", async () => {
  const field = document.getElementById("drive-normalized-url");
  try {
    await navigator.clipboard.writeText(field.value);
    setStatus(document.getElementById("drive-status"), "Đã sao chép đường dẫn ảnh.", "success");
  } catch (_) {
    field.select();
    document.execCommand("copy");
    setStatus(document.getElementById("drive-status"), "Đã sao chép đường dẫn ảnh.", "success");
  }
});

document.getElementById("home-logo").addEventListener("input", (event) => {
  document.getElementById("home-logo-preview").src = normalizeAssetUrl(event.target.value.trim());
});

document.getElementById("upload-home-logo").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const status = document.getElementById("homepage-status");
  try {
    setStatus(status, "Đang tải logo...");
    await uploadFile(file, (data) => {
      document.getElementById("home-logo").value = data.path;
      document.getElementById("home-logo-preview").src = data.url;
      document.getElementById("home-logo-size").textContent =
        `Khổ ảnh: ${data.size_label || formatSizeLabel(data.width, data.height)}`;
      setStatus(status, "Đã tải logo", "success");
    });
  } catch (error) {
    setStatus(status, error.message, "error");
  } finally {
    event.target.value = "";
  }
});

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
    if (view === "pages") {
      history.replaceState(null, "", " ");
      showView("pages");
    }
    if (view === "homepage") {
      await openHomepage();
    }
    if (view === "feedback") {
      await openFeedback();
    }
    if (view === "classes") {
      await openClasses();
    }
    if (view === "featured-cam-ket") {
      await openFeaturedCamKet();
    }
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

window.addEventListener("hashchange", () => {
  openFromHash().catch(() => {});
});

checkSession().catch(() => {});
