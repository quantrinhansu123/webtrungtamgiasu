# Trí Việt CMS

Plugin WordPress cung cấp bảng quản trị nội dung đơn giản cho website
`giasusuphamtriviet.vn`.

## Chức năng

- Tổng quan website.
- Cài đặt tên website, khẩu hiệu, hotline, Zalo và logo.
- Quản lý an toàn thông tin cơ bản của trang chủ Flatsome.
- Đăng và chỉnh sửa bài “Lớp mới”.
- Chọn ảnh phản hồi trực tiếp từ WordPress Media.
- Danh sách Trang và Thư viện ảnh.
- Shortcode `[tri_viet_feedback]` và
  `[tri_viet_feedback group="homepage"]`.

## Nguyên tắc an toàn

- Không thay đổi `siteurl` hoặc `home`.
- Không ghi đè shortcode Flatsome/UX Builder của trang chủ.
- Không xoá dữ liệu khi tắt hoặc gỡ plugin.
- Mọi thao tác lưu đều yêu cầu quyền `manage_options` và WordPress nonce.
- Thư viện phản hồi không tự hiển thị cho đến khi quản trị viên chủ động bật.

## Cài đặt

1. Sao lưu cơ sở dữ liệu và thư mục `wp-content`.
2. Tải thư mục `tri-viet-cms` vào `wp-content/plugins/`.
3. Kích hoạt **Trí Việt CMS** tại trang Plugins.
4. Mở menu **Trí Việt CMS** trong `wp-admin`.

Tài khoản WordPress hiện tại không có quyền cài hoặc sửa plugin. Cần tài
khoản có quyền `install_plugins`, hoặc quyền cPanel/SFTP/FTP để tải plugin.
