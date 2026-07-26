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
    repairAlreadyFailedImages();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
}());
