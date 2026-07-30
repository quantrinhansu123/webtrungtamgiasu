(function ($) {
  "use strict";

  function mediaField(button) {
    return button.closest(".tvcms-media-field");
  }

  function renderPreview(field, attachment) {
    var preview = field.find(".tvcms-media-preview");
    var source =
      attachment.sizes && attachment.sizes.medium
        ? attachment.sizes.medium.url
        : attachment.url;
    preview.empty().append($("<img>", { src: source, alt: "" }));
    field.find(".tvcms-media-id").val(attachment.id);
  }

  $(document).on("click", ".tvcms-media-select", function (event) {
    event.preventDefault();
    var button = $(this);
    var field = mediaField(button);
    var frame = wp.media({
      title: TriVietCMS.mediaTitle,
      button: { text: TriVietCMS.mediaButton },
      library: { type: "image" },
      multiple: false,
    });

    frame.on("select", function () {
      var attachment = frame.state().get("selection").first().toJSON();
      renderPreview(field, attachment);
    });
    frame.open();
  });

  $(document).on("click", ".tvcms-media-remove", function (event) {
    event.preventDefault();
    var field = mediaField($(this));
    field.find(".tvcms-media-id").val("");
    field
      .find(".tvcms-media-preview")
      .empty()
      .append($("<span>").text("Chưa chọn ảnh"));
  });
})(jQuery);
