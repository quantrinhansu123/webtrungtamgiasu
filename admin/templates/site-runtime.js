(function () {
  "use strict";

  var siteConfig = __SITE_CONFIG_JSON__;
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
    repairAlreadyFailedImages();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
}());
