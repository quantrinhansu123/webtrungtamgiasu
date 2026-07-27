(function () {
  "use strict";

  var siteConfig = {"site_name":"Trung Tâm Gia Sư Trí Việt","logo":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/b60442c2c31d48ab8146e213a27ac28c.jpg","hotline1":"0962.005.996","hotline2":"0987.005.996","feedback_images":[{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/feedback/fb1.jpg","alt":"Phản hồi của phụ huynh về gia sư Trí Việt 1"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/feedback/fb2.jpg","alt":"Phản hồi của phụ huynh về gia sư Trí Việt 2"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/feedback/fb3.jpg","alt":"Phản hồi của phụ huynh về gia sư Trí Việt 3"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/feedback/fb4.jpg","alt":"Phản hồi của phụ huynh về gia sư Trí Việt 4"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/feedback/fb5.jpg","alt":"Phản hồi của phụ huynh về gia sư Trí Việt 5"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/feedback/fb6.jpg","alt":"Phản hồi của phụ huynh về gia sư Trí Việt 6"}],"homepage_feedback_images":[{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-01.jpg","alt":"Phản hồi phụ huynh 1"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-02.jpg","alt":"Phản hồi phụ huynh 2"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-03.jpg","alt":"Phản hồi phụ huynh 3"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-04.jpg","alt":"Phản hồi phụ huynh 4"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-05.jpg","alt":"Phản hồi phụ huynh 5"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-06.jpg","alt":"Phản hồi phụ huynh 6"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-08.jpg","alt":"Phản hồi phụ huynh 8"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-09.jpg","alt":"Phản hồi phụ huynh 9"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-10.jpg","alt":"Phản hồi phụ huynh 10"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-11.jpg","alt":"Phản hồi phụ huynh 11"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-12.jpg","alt":"Phản hồi phụ huynh 12"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-13.jpg","alt":"Phản hồi phụ huynh 13"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-14.jpg","alt":"Phản hồi phụ huynh 14"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-15.jpg","alt":"Phản hồi phụ huynh 15"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-16.jpg","alt":"Phản hồi phụ huynh 16"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-17.jpg","alt":"Phản hồi phụ huynh 17"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-18.jpg","alt":"Phản hồi phụ huynh 18"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-19.jpg","alt":"Phản hồi phụ huynh 19"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-20.jpg","alt":"Phản hồi phụ huynh 20"},{"url":"/giasubinhminh.com/wp-content/uploads/cms/2026/07/phu-huynh-phan-hoi/phan-hoi-21.jpg","alt":"Phản hồi phụ huynh 21"}]};
  var runtimeScript = document.currentScript;
  var runtimeSrc = runtimeScript ? String(runtimeScript.getAttribute("src") || "") : "";
  var sitePrefix = (
    window.location.pathname.indexOf("/giasubinhminh.com/") === 0 ||
    runtimeSrc.indexOf("/giasubinhminh.com/") >= 0
  ) ? "/giasubinhminh.com" : "";
  var fallbackSrc = sitePrefix + "/wp-content/uploads/cms/2026/07/banner-trung-tam-gia-su-tri-viet.png";
  var textbookCovers = {
    "gia-su-van-10-de-thanh-cong-noi-tiep-thanh-cong": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/ngu-van-10-gdpt-2018.jpg",
      alt: "Sách giáo khoa Ngữ văn 10 - Chương trình GDPT 2018"
    },
    "gia-su-van-11-danh-thuc-dam-me-hoc-van-trong-con-nguoi-ban": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/ngu-van-11-gdpt-2018.jpg",
      alt: "Sách giáo khoa Ngữ văn 11 - Chương trình GDPT 2018"
    },
    "gia-su-van-lop-12-cham-dinh-cua-thanh-cong": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/ngu-van-12-gdpt-2018.webp",
      alt: "Sách giáo khoa Ngữ văn 12 - Chương trình GDPT 2018"
    },
    "gia-su-hoa-lop-10-giup-con-tro-thanh-than-dong-hoa-hoc": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/hoa-hoc-10-gdpt-2018.jpg",
      alt: "Sách giáo khoa Hóa học 10 - Chương trình GDPT 2018"
    },
    "gia-su-hoa-lop-11-de-con-duong-gioi-hoa-tro-nen-ngan-nhat": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/hoa-hoc-11-gdpt-2018.jpg",
      alt: "Sách giáo khoa Hóa học 11 - Chương trình GDPT 2018"
    },
    "gia-su-hoa-lop-12-muon-gioi-hoa-thi-khong-duoc-bo-lo": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/hoa-hoc-12-gdpt-2018.png",
      alt: "Sách giáo khoa Hóa học 12 - Chương trình GDPT 2018"
    },
    "gia-su-ly-lop-10-hoc-phi-re-hieu-qua-gap-3-lan": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/vat-ly-10-gdpt-2018.jpg",
      alt: "Sách giáo khoa Vật lí 10 - Chương trình GDPT 2018"
    },
    "gia-su-ly-lop-11-nam-giu-chia-khoa-cua-su-thanh-cong": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/vat-ly-11-gdpt-2018.jpg",
      alt: "Sách giáo khoa Vật lí 11 - Chương trình GDPT 2018"
    },
    "gia-su-ly-lop-12-nguoc-dong-de-chiem-linh-uoc-mo": {
      src: "/giasubinhminh.com/wp-content/uploads/cms/2026/07/sach-giao-khoa-moi/vat-ly-12-gdpt-2018.jpg",
      alt: "Sách giáo khoa Vật lí 12 - Chương trình GDPT 2018"
    }
  };
  var parentRequestImageCount = 50;
  var parentRequestAutoplayDelay = 5000;
  var parentRequestImageBase = (
    "/giasubinhminh.com/wp-content/uploads/cms/2026/07/" +
    "yeu-cau-tim-gia-su/yeu-cau-tim-gia-su-"
  );

  function safeImageUrl(value) {
    var url = String(value || "").trim();
    if (!url) return "";
    if (/^https:\/\//i.test(url) || url.indexOf("/") === 0) return url;
    if (/^[a-z][a-z0-9+.-]*:/i.test(url)) return "";
    return sitePrefix + "/" + url.replace(/^\/+/, "");
  }

  function replaceText(selector, value) {
    if (!value) return;
    Array.prototype.forEach.call(document.querySelectorAll(selector), function (node) {
      node.textContent = value;
    });
  }

  function textbookCoverForPath(pathname) {
    var normalizedPath = String(pathname || "").replace(/\/index\.html\/?$/i, "/");
    var slugs = Object.keys(textbookCovers);
    for (var index = 0; index < slugs.length; index += 1) {
      if (normalizedPath.indexOf("/" + slugs[index] + "/") >= 0) {
        return textbookCovers[slugs[index]];
      }
    }
    return null;
  }

  function applyTextbookCover(image, cover) {
    if (!image || !cover) return;
    var source = safeImageUrl(cover.src);
    if (!source) return;
    image.removeAttribute("srcset");
    image.removeAttribute("sizes");
    image.removeAttribute("width");
    image.removeAttribute("height");
    image.src = source;
    image.alt = cover.alt;
    image.dataset.triVietTextbookCover = "true";
  }

  function updateTextbookCovers() {
    Array.prototype.forEach.call(
      document.querySelectorAll("a[href] img"),
      function (image) {
        var link = image.closest("a[href]");
        if (!link) return;
        var pathname;
        try {
          pathname = new URL(link.href, window.location.href).pathname;
        } catch (_error) {
          return;
        }
        applyTextbookCover(image, textbookCoverForPath(pathname));
      }
    );

    var currentCover = textbookCoverForPath(window.location.pathname);
    if (currentCover) {
      applyTextbookCover(
        document.querySelector("article .entry-image img.wp-post-image"),
        currentCover
      );
    }
  }

  function isHomepage() {
    var pathname = String(window.location.pathname || "")
      .replace(/\/index\.html\/?$/i, "/")
      .replace(/\/+/g, "/");
    return (
      pathname === "/" ||
      pathname === "/giasubinhminh.com" ||
      pathname === "/giasubinhminh.com/"
    );
  }

  function findTutorRegistrationSection() {
    var matchedSpan = null;
    Array.prototype.some.call(
      document.querySelectorAll("a.button span, .button span"),
      function (span) {
        var label = String(span.textContent || "").trim().toLocaleLowerCase("vi");
        if (label.indexOf("đăng ký tìm gia sư") < 0) return false;
        matchedSpan = span;
        return true;
      }
    );
    return matchedSpan ? matchedSpan.closest("section") : null;
  }

  function addParentRequestCarouselStyles() {
    if (document.getElementById("tri-viet-parent-request-styles")) return;
    var style = document.createElement("style");
    style.id = "tri-viet-parent-request-styles";
    style.textContent = [
      ".tri-viet-parent-requests{box-sizing:border-box;background:",
      "linear-gradient(145deg,#f1faf6 0%,#fff 46%,#f4f8ff 100%);",
      "padding:64px 20px 72px;color:#17352a;border-top:1px solid #e2eee8;",
      "border-bottom:1px solid #e2eee8;font-family:Arial,sans-serif}",
      ".tri-viet-parent-requests *{box-sizing:border-box}",
      ".tri-viet-parent-requests__inner{max-width:1180px;margin:0 auto}",
      ".tri-viet-parent-requests__heading{text-align:center;margin:0 auto 32px;",
      "max-width:820px}",
      ".tri-viet-parent-requests__badge{display:inline-flex;align-items:center;",
      "gap:8px;margin:0 0 12px;padding:8px 16px;border-radius:999px;",
      "background:#dff3e9;color:#087849;font-size:14px;font-weight:700;",
      "letter-spacing:.04em;text-transform:uppercase}",
      ".tri-viet-parent-requests__badge:before{content:'';width:9px;height:9px;",
      "border-radius:50%;background:#0b8a55;box-shadow:0 0 0 4px #bce5d1}",
      ".tri-viet-parent-requests__title{margin:0;color:#0b7448;",
      "font-size:clamp(27px,3vw,42px);line-height:1.16;font-weight:800}",
      ".tri-viet-parent-requests__subtitle{margin:12px auto 0;color:#435c52;",
      "font-size:17px;line-height:1.65;max-width:720px}",
      ".tri-viet-parent-requests__shell{position:relative;padding:0 58px}",
      ".tri-viet-parent-requests__track{display:flex;gap:18px;margin:0;",
      "padding:10px 4px 22px;overflow-x:auto;scroll-snap-type:x mandatory;",
      "scroll-behavior:smooth;scrollbar-width:none;-ms-overflow-style:none;",
      "overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch;",
      "touch-action:pan-x;cursor:grab}",
      ".tri-viet-parent-requests__track::-webkit-scrollbar{display:none}",
      ".tri-viet-parent-requests__track.is-dragging{cursor:grabbing;",
      "scroll-snap-type:none;user-select:none}",
      ".tri-viet-parent-requests__slide{flex:0 0 calc((100% - 36px)/3);",
      "min-width:0;margin:0;padding:10px;border:1px solid #d9e7e0;",
      "border-radius:20px;background:#fff;color:#183a2d;",
      "box-shadow:0 12px 32px rgba(20,72,51,.12);scroll-snap-align:start;",
      "cursor:zoom-in;text-align:left;appearance:none;-webkit-appearance:none;",
      "transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}",
      ".tri-viet-parent-requests__slide:hover{transform:translateY(-4px);",
      "border-color:#7bc4a3;box-shadow:0 18px 38px rgba(20,72,51,.18)}",
      ".tri-viet-parent-requests__slide:focus-visible,",
      ".tri-viet-parent-requests__control:focus-visible,",
      ".tri-viet-parent-requests__close:focus-visible{outline:3px solid #ffb000;",
      "outline-offset:3px}",
      ".tri-viet-parent-requests__image-wrap{display:block;overflow:hidden;",
      "border-radius:13px;background:#eaf3ef;aspect-ratio:870/1883}",
      ".tri-viet-parent-requests__image{display:block;width:100%;height:100%;",
      "object-fit:contain;background:#edf4f1}",
      ".tri-viet-parent-requests__caption{display:flex;align-items:center;",
      "justify-content:space-between;gap:10px;padding:13px 4px 5px;",
      "font-size:15px;line-height:1.4;font-weight:700}",
      ".tri-viet-parent-requests__caption small{color:#0b8150;font-size:13px;",
      "font-weight:700;white-space:nowrap}",
      ".tri-viet-parent-requests__control{position:absolute;z-index:2;top:47%;",
      "width:46px;height:46px;min-width:0;min-height:0;max-width:none;",
      "margin:0;padding:0;border:0;border-radius:50%;background:#087849;",
      "color:#fff;font-size:34px;line-height:42px;text-align:center;",
      "box-shadow:0 8px 22px rgba(8,83,52,.25);cursor:pointer;",
      "transition:background .2s ease,transform .2s ease}",
      ".tri-viet-parent-requests__control:hover{background:#075f3b;",
      "transform:scale(1.06)}",
      ".tri-viet-parent-requests__control--prev{left:0}",
      ".tri-viet-parent-requests__control--next{right:0}",
      ".tri-viet-parent-requests__footer{display:flex;align-items:center;",
      "justify-content:center;gap:13px;margin-top:8px;color:#496158;",
      "font-size:14px;font-weight:600}",
      ".tri-viet-parent-requests__counter{min-width:72px;padding:8px 12px;",
      "border-radius:999px;background:#087849;color:#fff;text-align:center;",
      "font-variant-numeric:tabular-nums}",
      ".tri-viet-parent-requests__hint{margin:0}",
      ".tri-viet-parent-requests__lightbox{position:fixed;z-index:999999;",
      "inset:0;display:none;align-items:center;justify-content:center;",
      "padding:24px;background:rgba(4,20,14,.94)}",
      ".tri-viet-parent-requests__lightbox.is-open{display:flex}",
      ".tri-viet-parent-requests__lightbox-image{display:block;max-width:",
      "min(94vw,870px);max-height:92vh;width:auto;height:auto;object-fit:contain;",
      "border-radius:12px;background:#fff;box-shadow:0 24px 80px #000}",
      ".tri-viet-parent-requests__close{position:fixed;z-index:1;top:18px;",
      "right:18px;width:48px;height:48px;min-width:0;min-height:0;max-width:none;",
      "margin:0;padding:0;border:2px solid rgba(255,255,255,.5);",
      "border-radius:50%;background:#087849;color:#fff;font-size:31px;",
      "line-height:40px;cursor:pointer}",
      "@media(max-width:900px){.tri-viet-parent-requests__slide{",
      "flex-basis:calc((100% - 18px)/2)}}",
      "@media(max-width:600px){.tri-viet-parent-requests{padding:45px 14px 52px}",
      ".tri-viet-parent-requests__heading{margin-bottom:22px}",
      ".tri-viet-parent-requests__subtitle{font-size:15px}",
      ".tri-viet-parent-requests__shell{padding:0 0 58px}",
      ".tri-viet-parent-requests__track{gap:12px;padding:8px 5px 18px}",
      ".tri-viet-parent-requests__slide{flex-basis:calc(100% - 28px);",
      "padding:8px;border-radius:17px}",
      ".tri-viet-parent-requests__control{top:auto;bottom:7px;width:44px;",
      "height:44px;font-size:30px;line-height:39px}",
      ".tri-viet-parent-requests__control--prev{left:calc(50% - 106px)}",
      ".tri-viet-parent-requests__control--next{right:calc(50% - 106px)}",
      ".tri-viet-parent-requests__footer{position:relative;min-height:58px;",
      "margin-top:-58px;padding-top:7px;gap:11px;flex-wrap:wrap}",
      ".tri-viet-parent-requests__hint{flex-basis:100%;text-align:center;",
      "margin-top:9px}}",
      "@media(prefers-reduced-motion:reduce){.tri-viet-parent-requests__track{",
      "scroll-behavior:auto}.tri-viet-parent-requests__slide,",
      ".tri-viet-parent-requests__control{transition:none}}"
    ].join("");
    document.head.appendChild(style);
  }

  function initializeParentRequestCarousel() {
    if (!isHomepage()) return;
    if (document.getElementById("tri-viet-parent-requests")) return;

    var registrationSection = findTutorRegistrationSection();
    if (!registrationSection) return;

    addParentRequestCarouselStyles();

    var section = document.createElement("section");
    section.id = "tri-viet-parent-requests";
    section.className = "tri-viet-parent-requests";
    section.setAttribute("aria-labelledby", "tri-viet-parent-requests-title");

    var inner = document.createElement("div");
    inner.className = "tri-viet-parent-requests__inner";
    inner.innerHTML = [
      '<header class="tri-viet-parent-requests__heading">',
      '<p class="tri-viet-parent-requests__badge">50 yêu cầu thực tế</p>',
      '<h2 class="tri-viet-parent-requests__title" ',
      'id="tri-viet-parent-requests-title">',
      "Phụ huynh đăng ký tìm gia sư</h2>",
      '<p class="tri-viet-parent-requests__subtitle">',
      "Nhu cầu học tập được Trung Tâm Gia Sư Trí Việt tiếp nhận trực tiếp. ",
      "Vuốt sang ngang hoặc dùng nút điều hướng để xem.</p>",
      "</header>"
    ].join("");

    var shell = document.createElement("div");
    shell.className = "tri-viet-parent-requests__shell";

    var track = document.createElement("div");
    track.className = "tri-viet-parent-requests__track";
    track.setAttribute("role", "region");
    track.setAttribute("aria-roledescription", "carousel");
    track.setAttribute("aria-label", "Yêu cầu tìm gia sư từ phụ huynh");
    track.setAttribute("tabindex", "0");

    var slides = [];
    for (var index = 1; index <= parentRequestImageCount; index += 1) {
      var number = String(index).padStart(2, "0");
      var slide = document.createElement("button");
      slide.type = "button";
      slide.className = "tri-viet-parent-requests__slide";
      slide.setAttribute("aria-label", "Xem lớn yêu cầu tìm gia sư " + index);

      var imageWrap = document.createElement("span");
      imageWrap.className = "tri-viet-parent-requests__image-wrap";
      var image = document.createElement("img");
      image.className = "tri-viet-parent-requests__image";
      image.src = parentRequestImageBase + number + ".jpg";
      image.alt = "Tin nhắn phụ huynh đăng ký tìm gia sư " + index;
      image.loading = index <= 6 ? "eager" : "lazy";
      image.decoding = "async";
      imageWrap.appendChild(image);

      var caption = document.createElement("span");
      caption.className = "tri-viet-parent-requests__caption";
      caption.innerHTML = (
        "<span>Yêu cầu phụ huynh " + number + "</span>" +
        "<small>Chạm để xem rõ</small>"
      );
      slide.appendChild(imageWrap);
      slide.appendChild(caption);
      track.appendChild(slide);
      slides.push(slide);
    }

    var previous = document.createElement("button");
    previous.type = "button";
    previous.className = (
      "tri-viet-parent-requests__control " +
      "tri-viet-parent-requests__control--prev"
    );
    previous.setAttribute("aria-label", "Xem ảnh trước");
    previous.textContent = "\u2039";

    var next = document.createElement("button");
    next.type = "button";
    next.className = (
      "tri-viet-parent-requests__control " +
      "tri-viet-parent-requests__control--next"
    );
    next.setAttribute("aria-label", "Xem ảnh tiếp theo");
    next.textContent = "\u203a";

    var footer = document.createElement("div");
    footer.className = "tri-viet-parent-requests__footer";
    var counter = document.createElement("span");
    counter.className = "tri-viet-parent-requests__counter";
    counter.setAttribute("aria-label", "Vị trí ảnh");
    counter.textContent = "01 / 50";
    var hint = document.createElement("p");
    hint.className = "tri-viet-parent-requests__hint";
    hint.textContent = "Tự chuyển sau mỗi 5 giây \u00b7 Có thể vuốt sang ngang";
    footer.appendChild(counter);
    footer.appendChild(hint);

    shell.appendChild(previous);
    shell.appendChild(track);
    shell.appendChild(next);
    inner.appendChild(shell);
    inner.appendChild(footer);
    section.appendChild(inner);
    registrationSection.insertAdjacentElement("afterend", section);

    var lightbox = document.createElement("div");
    lightbox.className = "tri-viet-parent-requests__lightbox";
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");
    lightbox.setAttribute("aria-label", "Xem rõ yêu cầu tìm gia sư");
    lightbox.setAttribute("aria-hidden", "true");
    var lightboxImage = document.createElement("img");
    lightboxImage.className = "tri-viet-parent-requests__lightbox-image";
    lightboxImage.alt = "";
    var close = document.createElement("button");
    close.type = "button";
    close.className = "tri-viet-parent-requests__close";
    close.setAttribute("aria-label", "Đóng ảnh");
    close.textContent = "\u00d7";
    lightbox.appendChild(lightboxImage);
    lightbox.appendChild(close);
    document.body.appendChild(lightbox);

    var currentIndex = 0;
    var autoplayTimer = null;
    var scrollTimer = null;
    var programmaticScrollTimer = null;
    var programmaticScrolling = false;
    var lastFocusedElement = null;
    var reducedMotion = (
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );

    function updateCounter() {
      counter.textContent = (
        String(currentIndex + 1).padStart(2, "0") +
        " / " +
        parentRequestImageCount
      );
    }

    function goTo(targetIndex, behavior) {
      currentIndex = (
        (targetIndex % parentRequestImageCount) + parentRequestImageCount
      ) % parentRequestImageCount;
      for (var preloadOffset = 0; preloadOffset < 4; preloadOffset += 1) {
        var preloadIndex = (
          currentIndex + preloadOffset
        ) % parentRequestImageCount;
        var preloadImage = slides[preloadIndex].querySelector("img");
        if (preloadImage) preloadImage.loading = "eager";
      }
      var firstOffset = slides[0] ? slides[0].offsetLeft : 0;
      programmaticScrolling = true;
      if (programmaticScrollTimer) {
        window.clearTimeout(programmaticScrollTimer);
      }
      track.scrollTo({
        left: slides[currentIndex].offsetLeft - firstOffset,
        behavior: behavior || "smooth"
      });
      programmaticScrollTimer = window.setTimeout(function () {
        programmaticScrolling = false;
      }, 700);
      updateCounter();
    }

    function stopAutoplay() {
      if (autoplayTimer) window.clearInterval(autoplayTimer);
      autoplayTimer = null;
    }

    function startAutoplay() {
      stopAutoplay();
      if (reducedMotion || document.hidden) return;
      autoplayTimer = window.setInterval(function () {
        goTo(currentIndex + 1, "smooth");
      }, parentRequestAutoplayDelay);
    }

    function restartAutoplay() {
      stopAutoplay();
      startAutoplay();
    }

    function syncIndexAfterScroll() {
      if (programmaticScrolling) return;
      if (scrollTimer) window.clearTimeout(scrollTimer);
      scrollTimer = window.setTimeout(function () {
        var firstOffset = slides[0] ? slides[0].offsetLeft : 0;
        var nearestIndex = 0;
        var nearestDistance = Infinity;
        slides.forEach(function (slide, slideIndex) {
          var distance = Math.abs(
            track.scrollLeft - (slide.offsetLeft - firstOffset)
          );
          if (distance < nearestDistance) {
            nearestDistance = distance;
            nearestIndex = slideIndex;
          }
        });
        currentIndex = nearestIndex;
        updateCounter();
      }, 90);
    }

    previous.addEventListener("click", function () {
      goTo(currentIndex - 1, "smooth");
      restartAutoplay();
    });
    next.addEventListener("click", function () {
      goTo(currentIndex + 1, "smooth");
      restartAutoplay();
    });
    track.addEventListener("scroll", syncIndexAfterScroll, { passive: true });
    track.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      goTo(currentIndex + (event.key === "ArrowRight" ? 1 : -1), "smooth");
      restartAutoplay();
    });
    track.addEventListener("mouseenter", stopAutoplay);
    track.addEventListener("mouseleave", startAutoplay);
    track.addEventListener("focusin", stopAutoplay);
    track.addEventListener("focusout", function (event) {
      if (!track.contains(event.relatedTarget)) startAutoplay();
    });
    track.addEventListener("touchstart", function () {
      programmaticScrolling = false;
      if (programmaticScrollTimer) {
        window.clearTimeout(programmaticScrollTimer);
      }
      stopAutoplay();
    }, { passive: true });
    track.addEventListener("touchend", restartAutoplay, { passive: true });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stopAutoplay();
      else startAutoplay();
    });

    var dragging = false;
    var blockSlideClick = false;
    var dragStartX = 0;
    var dragStartScroll = 0;
    track.addEventListener("pointerdown", function (event) {
      if (event.pointerType !== "mouse" || event.button !== 0) return;
      dragging = true;
      blockSlideClick = false;
      programmaticScrolling = false;
      if (programmaticScrollTimer) {
        window.clearTimeout(programmaticScrollTimer);
      }
      dragStartX = event.clientX;
      dragStartScroll = track.scrollLeft;
      track.classList.add("is-dragging");
      track.setPointerCapture(event.pointerId);
      stopAutoplay();
    });
    track.addEventListener("pointermove", function (event) {
      if (!dragging) return;
      event.preventDefault();
      if (Math.abs(event.clientX - dragStartX) > 5) blockSlideClick = true;
      track.scrollLeft = dragStartScroll - (event.clientX - dragStartX);
    });
    function finishDragging(event) {
      if (!dragging) return;
      dragging = false;
      track.classList.remove("is-dragging");
      if (track.hasPointerCapture(event.pointerId)) {
        track.releasePointerCapture(event.pointerId);
      }
      syncIndexAfterScroll();
      restartAutoplay();
      window.setTimeout(function () {
        blockSlideClick = false;
      }, 50);
    }
    track.addEventListener("pointerup", finishDragging);
    track.addEventListener("pointercancel", finishDragging);

    function closeLightbox() {
      lightbox.classList.remove("is-open");
      lightbox.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
      lightboxImage.removeAttribute("src");
      if (lastFocusedElement) lastFocusedElement.focus();
      startAutoplay();
    }

    slides.forEach(function (slide, slideIndex) {
      slide.addEventListener("click", function () {
        if (blockSlideClick || track.classList.contains("is-dragging")) return;
        currentIndex = slideIndex;
        updateCounter();
        lastFocusedElement = slide;
        lightboxImage.src = slide.querySelector("img").src;
        lightboxImage.alt = slide.querySelector("img").alt;
        lightbox.classList.add("is-open");
        lightbox.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        stopAutoplay();
        close.focus();
      });
    });
    close.addEventListener("click", closeLightbox);
    lightbox.addEventListener("click", function (event) {
      if (event.target === lightbox) closeLightbox();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && lightbox.classList.contains("is-open")) {
        closeLightbox();
      }
    });

    updateCounter();
    startAutoplay();
  }

  function updateHeader(config) {
    var siteName = String(config.site_name || "").trim();
    var logo = safeImageUrl(config.logo);
    var hotline1 = String(config.hotline1 || "").trim();
    var hotline2 = String(config.hotline2 || "").trim();

    replaceText(".header-top-heading h3", siteName);

    Array.prototype.forEach.call(
      document.querySelectorAll(".header_logo, .header-logo, .header-logo-dark"),
      function (image) {
        if (logo) {
          image.removeAttribute("srcset");
          image.removeAttribute("sizes");
          image.src = logo;
        }
        if (siteName) image.alt = siteName;
      }
    );

    Array.prototype.forEach.call(document.querySelectorAll('#logo a[rel="home"]'), function (link) {
      if (siteName) link.title = siteName;
    });

    var hotlineButtons = document.querySelectorAll(".header-button a.button");
    [hotline1, hotline2].forEach(function (phone, index) {
      if (!phone || !hotlineButtons[index]) return;
      var label = hotlineButtons[index].querySelector("span");
      if (label) label.textContent = "Hotline : " + phone;
      hotlineButtons[index].href = "tel:" + phone.replace(/\D/g, "");
    });
  }

  function applyFeedbackItems(images, links, feedback) {
    feedback.forEach(function (item, index) {
      var image = images[index];
      var url = safeImageUrl(item && item.url);
      if (!url || !image) return;
      image.removeAttribute("srcset");
      image.removeAttribute("sizes");
      image.src = url;
      image.alt = String(
        (item && item.alt) ||
        ("Phản hồi của phụ huynh về gia sư Trí Việt " + (index + 1))
      );
      if (links[index]) links[index].href = url;
    });
  }

  function updateFeedback(config) {
    var homepageFeedback = Array.isArray(config.homepage_feedback_images)
      ? config.homepage_feedback_images
      : [];
    var homepageImages = document.querySelectorAll(".testimonial-collage img");
    var homepageLinks = document.querySelectorAll(".testimonial-collage a");
    applyFeedbackItems(homepageImages, homepageLinks, homepageFeedback);

    var sharedFeedback = Array.isArray(config.feedback_images)
      ? config.feedback_images
      : [];
    Array.prototype.forEach.call(
      document.querySelectorAll(
        ".tri-viet-feedback-gallery, #parent-feedback-gallery"
      ),
      function (gallery) {
        applyFeedbackItems(
          gallery.querySelectorAll("img"),
          gallery.querySelectorAll("a"),
          sharedFeedback
        );
      }
    );
  }

  function applySiteConfig(config) {
    if (!config || typeof config !== "object") return;
    updateHeader(config);
    updateFeedback(config);
  }

  function applyFallback(image) {
    if (!image || image.dataset.triVietFallback === "true") return;
    image.dataset.triVietFallback = "true";
    image.removeAttribute("srcset");
    image.removeAttribute("sizes");
    image.src = fallbackSrc;
    image.alt = image.alt || "Trung Tâm Gia Sư Trí Việt";
  }

  document.addEventListener("error", function (event) {
    if (event.target && event.target.tagName === "IMG") {
      applyFallback(event.target);
    }
  }, true);

  function repairAlreadyFailedImages() {
    Array.prototype.forEach.call(document.images, function (image) {
      if (image.complete && image.naturalWidth === 0) applyFallback(image);
    });
  }

  function initialize() {
    applySiteConfig(siteConfig);
    updateTextbookCovers();
    initializeParentRequestCarousel();
    repairAlreadyFailedImages();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
}());
