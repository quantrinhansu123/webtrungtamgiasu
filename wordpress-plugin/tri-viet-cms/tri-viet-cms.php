<?php
/**
 * Plugin Name: Trí Việt CMS
 * Description: Bảng quản trị nội dung đơn giản dành cho Trung Tâm Gia Sư Trí Việt.
 * Version: 1.0.0
 * Author: Trí Việt
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * Text Domain: tri-viet-cms
 */

if (!defined('ABSPATH')) {
    exit;
}

final class Tri_Viet_CMS
{
    const VERSION = '1.0.0';
    const SLUG = 'tri-viet-cms';
    const CAPABILITY = 'manage_options';
    const OPTION_HOTLINE_1 = 'tvcms_hotline_1';
    const OPTION_HOTLINE_2 = 'tvcms_hotline_2';
    const OPTION_ZALO = 'tvcms_zalo_url';
    const OPTION_FEEDBACK = 'tvcms_feedback_ids';
    const OPTION_HOMEPAGE_FEEDBACK = 'tvcms_homepage_feedback_ids';
    const OPTION_FEEDBACK_ENABLED = 'tvcms_feedback_enabled';

    private static $instance = null;
    private $hook_suffix = '';

    public static function instance()
    {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public static function activate()
    {
        add_option(self::OPTION_HOTLINE_1, '0962.005.996');
        add_option(self::OPTION_HOTLINE_2, '');
        add_option(self::OPTION_ZALO, '');
        add_option(self::OPTION_FEEDBACK, array());
        add_option(self::OPTION_HOMEPAGE_FEEDBACK, array());
        add_option(self::OPTION_FEEDBACK_ENABLED, '0');
    }

    private function __construct()
    {
        add_action('admin_menu', array($this, 'register_menu'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_assets'));
        add_action('admin_post_tvcms_save_settings', array($this, 'save_settings'));
        add_action('admin_post_tvcms_save_homepage', array($this, 'save_homepage'));
        add_action('admin_post_tvcms_save_class', array($this, 'save_class'));
        add_action('admin_post_tvcms_save_feedback', array($this, 'save_feedback'));
        add_shortcode('tri_viet_feedback', array($this, 'feedback_shortcode'));
        add_filter('the_content', array($this, 'maybe_append_homepage_feedback'), 20);
    }

    public function register_menu()
    {
        $this->hook_suffix = add_menu_page(
            'Trí Việt CMS',
            'Trí Việt CMS',
            self::CAPABILITY,
            self::SLUG,
            array($this, 'render_admin'),
            'dashicons-welcome-learn-more',
            3
        );
    }

    public function enqueue_admin_assets($hook_suffix)
    {
        if ($hook_suffix !== $this->hook_suffix) {
            return;
        }

        wp_enqueue_media();
        wp_enqueue_editor();
        wp_enqueue_style(
            'tvcms-admin',
            plugin_dir_url(__FILE__) . 'assets/admin.css',
            array(),
            self::VERSION
        );
        wp_enqueue_script(
            'tvcms-admin',
            plugin_dir_url(__FILE__) . 'assets/admin.js',
            array('jquery'),
            self::VERSION,
            true
        );
        wp_localize_script(
            'tvcms-admin',
            'TriVietCMS',
            array(
                'mediaTitle' => 'Chọn ảnh',
                'mediaButton' => 'Sử dụng ảnh này',
            )
        );
    }

    private function require_permission()
    {
        if (!current_user_can(self::CAPABILITY)) {
            wp_die(esc_html__('Bạn không có quyền sử dụng chức năng này.', 'tri-viet-cms'));
        }
    }

    private function admin_url_for($view = 'dashboard', $args = array())
    {
        $query = array_merge(
            array(
                'page' => self::SLUG,
                'view' => $view,
            ),
            $args
        );
        return add_query_arg($query, admin_url('admin.php'));
    }

    private function redirect_with_notice($view, $notice, $extra = array())
    {
        $args = array_merge(array('tvcms_notice' => $notice), $extra);
        wp_safe_redirect($this->admin_url_for($view, $args));
        exit;
    }

    private function current_view()
    {
        $allowed = array(
            'dashboard',
            'homepage',
            'classes',
            'feedback',
            'pages',
            'media',
            'settings',
        );
        $view = isset($_GET['view'])
            ? sanitize_key(wp_unslash($_GET['view']))
            : 'dashboard';
        return in_array($view, $allowed, true) ? $view : 'dashboard';
    }

    private function navigation_items()
    {
        return array(
            'dashboard' => array('Tổng quan', 'dashicons-dashboard'),
            'homepage' => array('Trang chủ', 'dashicons-admin-home'),
            'classes' => array('Lớp mới', 'dashicons-welcome-write-blog'),
            'feedback' => array('Phản hồi phụ huynh', 'dashicons-format-gallery'),
            'pages' => array('Trang nội dung', 'dashicons-admin-page'),
            'media' => array('Thư viện ảnh', 'dashicons-format-image'),
            'settings' => array('Cài đặt chung', 'dashicons-admin-settings'),
        );
    }

    public function render_admin()
    {
        $this->require_permission();
        $view = $this->current_view();
        ?>
        <div class="wrap tvcms-wrap">
            <div class="tvcms-shell">
                <aside class="tvcms-sidebar">
                    <div class="tvcms-brand">
                        <span class="dashicons dashicons-welcome-learn-more"></span>
                        <div>
                            <strong>Trí Việt CMS</strong>
                            <small>Quản trị website</small>
                        </div>
                    </div>
                    <nav aria-label="Điều hướng Trí Việt CMS">
                        <?php foreach ($this->navigation_items() as $key => $item) : ?>
                            <a
                                class="<?php echo esc_attr($view === $key ? 'is-active' : ''); ?>"
                                href="<?php echo esc_url($this->admin_url_for($key)); ?>"
                            >
                                <span class="dashicons <?php echo esc_attr($item[1]); ?>"></span>
                                <?php echo esc_html($item[0]); ?>
                            </a>
                        <?php endforeach; ?>
                    </nav>
                    <div class="tvcms-sidebar-footer">
                        <a href="<?php echo esc_url(home_url('/')); ?>" target="_blank" rel="noopener">
                            <span class="dashicons dashicons-external"></span>
                            Mở website
                        </a>
                    </div>
                </aside>
                <main class="tvcms-main">
                    <?php $this->render_notice(); ?>
                    <?php
                    switch ($view) {
                        case 'homepage':
                            $this->render_homepage();
                            break;
                        case 'classes':
                            $this->render_classes();
                            break;
                        case 'feedback':
                            $this->render_feedback();
                            break;
                        case 'pages':
                            $this->render_pages();
                            break;
                        case 'media':
                            $this->render_media();
                            break;
                        case 'settings':
                            $this->render_settings();
                            break;
                        default:
                            $this->render_dashboard();
                    }
                    ?>
                </main>
            </div>
        </div>
        <?php
    }

    private function render_notice()
    {
        if (empty($_GET['tvcms_notice'])) {
            return;
        }
        $notice = sanitize_key(wp_unslash($_GET['tvcms_notice']));
        $messages = array(
            'settings-saved' => 'Đã lưu cài đặt website.',
            'homepage-saved' => 'Đã cập nhật thông tin trang chủ.',
            'class-saved' => 'Đã lưu lớp mới.',
            'feedback-saved' => 'Đã lưu thư viện phản hồi.',
            'invalid-request' => 'Dữ liệu không hợp lệ, vui lòng kiểm tra lại.',
            'save-failed' => 'Không thể lưu dữ liệu. Vui lòng thử lại.',
        );
        if (!isset($messages[$notice])) {
            return;
        }
        $is_error = in_array($notice, array('invalid-request', 'save-failed'), true);
        ?>
        <div class="notice <?php echo esc_attr($is_error ? 'notice-error' : 'notice-success'); ?> is-dismissible">
            <p><?php echo esc_html($messages[$notice]); ?></p>
        </div>
        <?php
    }

    private function render_page_header($eyebrow, $title, $description, $action = '')
    {
        ?>
        <header class="tvcms-page-header">
            <div>
                <span class="tvcms-eyebrow"><?php echo esc_html($eyebrow); ?></span>
                <h1><?php echo esc_html($title); ?></h1>
                <p><?php echo esc_html($description); ?></p>
            </div>
            <?php echo $action; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
        </header>
        <?php
    }

    private function count_class_posts()
    {
        $query = new WP_Query(
            array(
                'post_type' => 'post',
                'post_status' => array('publish', 'draft', 'pending', 'future'),
                'posts_per_page' => 1,
                's' => 'LỚP MỚI',
                'fields' => 'ids',
            )
        );
        return (int) $query->found_posts;
    }

    private function render_dashboard()
    {
        $page_count = wp_count_posts('page');
        $post_count = wp_count_posts('post');
        $feedback_count = count($this->get_attachment_ids(self::OPTION_HOMEPAGE_FEEDBACK, 20));
        $front_page_id = (int) get_option('page_on_front');
        $front_page = $front_page_id ? get_post($front_page_id) : null;

        $this->render_page_header(
            'TRÍ VIỆT CMS',
            'Quản lý website',
            'Chọn đúng mục cần sửa, kiểm tra lại nội dung rồi bấm Lưu.'
        );
        ?>
        <div class="tvcms-stats">
            <a href="<?php echo esc_url($this->admin_url_for('pages')); ?>">
                <span class="dashicons dashicons-admin-page"></span>
                <strong><?php echo esc_html((string) ((int) $page_count->publish)); ?></strong>
                <small>Trang đã xuất bản</small>
            </a>
            <a href="<?php echo esc_url($this->admin_url_for('classes')); ?>">
                <span class="dashicons dashicons-welcome-write-blog"></span>
                <strong><?php echo esc_html((string) $this->count_class_posts()); ?></strong>
                <small>Bài lớp mới</small>
            </a>
            <a href="<?php echo esc_url($this->admin_url_for('feedback')); ?>">
                <span class="dashicons dashicons-format-gallery"></span>
                <strong><?php echo esc_html((string) $feedback_count); ?></strong>
                <small>Ảnh phản hồi trang chủ</small>
            </a>
            <a href="<?php echo esc_url(admin_url('edit.php')); ?>">
                <span class="dashicons dashicons-admin-post"></span>
                <strong><?php echo esc_html((string) ((int) $post_count->publish)); ?></strong>
                <small>Bài viết</small>
            </a>
        </div>

        <div class="tvcms-grid tvcms-grid--two">
            <section class="tvcms-panel">
                <div class="tvcms-panel-heading">
                    <div>
                        <span class="dashicons dashicons-admin-home"></span>
                        <h2>Trang chủ đang dùng</h2>
                    </div>
                </div>
                <?php if ($front_page) : ?>
                    <h3><?php echo esc_html(get_the_title($front_page)); ?></h3>
                    <p>Trang chủ được dựng bằng Flatsome/UX Builder. Plugin không tự ghi đè nội dung bố cục.</p>
                    <div class="tvcms-actions">
                        <a class="button button-primary" href="<?php echo esc_url($this->admin_url_for('homepage')); ?>">
                            Quản lý trang chủ
                        </a>
                        <a class="button" href="<?php echo esc_url(get_edit_post_link($front_page_id)); ?>">
                            Mở trình sửa WordPress
                        </a>
                    </div>
                <?php else : ?>
                    <p>Website chưa chọn một trang tĩnh làm trang chủ.</p>
                <?php endif; ?>
            </section>

            <section class="tvcms-panel">
                <div class="tvcms-panel-heading">
                    <div>
                        <span class="dashicons dashicons-shield-alt"></span>
                        <h2>Trạng thái an toàn</h2>
                    </div>
                </div>
                <ul class="tvcms-checklist">
                    <li><span class="dashicons dashicons-yes-alt"></span> Dùng tài khoản và phân quyền WordPress</li>
                    <li><span class="dashicons dashicons-yes-alt"></span> Mọi biểu mẫu đều có mã bảo vệ nonce</li>
                    <li><span class="dashicons dashicons-yes-alt"></span> Không thay đổi WordPress URL hoặc Site URL</li>
                    <li><span class="dashicons dashicons-yes-alt"></span> Không ghi đè bố cục Flatsome</li>
                </ul>
            </section>
        </div>
        <?php
    }

    private function render_settings()
    {
        $logo_id = (int) get_theme_mod('custom_logo');
        $logo_url = $logo_id ? wp_get_attachment_image_url($logo_id, 'medium') : '';
        $this->render_page_header(
            'CÀI ĐẶT CHUNG',
            'Thông tin website',
            'Các thay đổi tại đây được lưu trực tiếp vào WordPress.'
        );
        ?>
        <form class="tvcms-panel tvcms-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
            <input type="hidden" name="action" value="tvcms_save_settings">
            <?php wp_nonce_field('tvcms_save_settings'); ?>
            <div class="tvcms-form-grid">
                <label>
                    <span>Tên website</span>
                    <input type="text" name="site_name" maxlength="160" required value="<?php echo esc_attr(get_option('blogname')); ?>">
                </label>
                <label>
                    <span>Khẩu hiệu</span>
                    <input type="text" name="tagline" maxlength="255" value="<?php echo esc_attr(get_option('blogdescription')); ?>">
                </label>
                <label>
                    <span>Hotline chính</span>
                    <input type="text" name="hotline_1" maxlength="50" value="<?php echo esc_attr(get_option(self::OPTION_HOTLINE_1)); ?>">
                </label>
                <label>
                    <span>Hotline phụ</span>
                    <input type="text" name="hotline_2" maxlength="50" value="<?php echo esc_attr(get_option(self::OPTION_HOTLINE_2)); ?>">
                </label>
                <label class="tvcms-field-wide">
                    <span>Đường dẫn Zalo</span>
                    <input type="url" name="zalo_url" value="<?php echo esc_attr(get_option(self::OPTION_ZALO)); ?>" placeholder="https://zalo.me/...">
                </label>
                <div class="tvcms-field-wide tvcms-media-field">
                    <span class="tvcms-label">Logo website</span>
                    <input class="tvcms-media-id" type="hidden" name="logo_id" value="<?php echo esc_attr((string) $logo_id); ?>">
                    <div class="tvcms-media-preview">
                        <?php if ($logo_url) : ?>
                            <img src="<?php echo esc_url($logo_url); ?>" alt="">
                        <?php else : ?>
                            <span>Chưa chọn logo</span>
                        <?php endif; ?>
                    </div>
                    <div class="tvcms-actions">
                        <button class="button tvcms-media-select" type="button">Chọn logo</button>
                        <button class="button tvcms-media-remove" type="button">Bỏ chọn</button>
                    </div>
                </div>
            </div>
            <div class="tvcms-safe-url">
                <span class="dashicons dashicons-lock"></span>
                <div>
                    <strong>Địa chỉ website được bảo vệ</strong>
                    <code><?php echo esc_html(home_url('/')); ?></code>
                    <p>Plugin không thay đổi WordPress Address hoặc Site Address.</p>
                </div>
            </div>
            <button class="button button-primary button-hero" type="submit">Lưu cài đặt</button>
        </form>
        <?php
    }

    public function save_settings()
    {
        $this->require_permission();
        check_admin_referer('tvcms_save_settings');

        $site_name = isset($_POST['site_name'])
            ? sanitize_text_field(wp_unslash($_POST['site_name']))
            : '';
        if ('' === $site_name) {
            $this->redirect_with_notice('settings', 'invalid-request');
        }

        $tagline = isset($_POST['tagline'])
            ? sanitize_text_field(wp_unslash($_POST['tagline']))
            : '';
        $hotline_1 = isset($_POST['hotline_1'])
            ? sanitize_text_field(wp_unslash($_POST['hotline_1']))
            : '';
        $hotline_2 = isset($_POST['hotline_2'])
            ? sanitize_text_field(wp_unslash($_POST['hotline_2']))
            : '';
        $zalo_url = isset($_POST['zalo_url'])
            ? esc_url_raw(wp_unslash($_POST['zalo_url']), array('http', 'https'))
            : '';
        $logo_id = isset($_POST['logo_id']) ? absint($_POST['logo_id']) : 0;

        update_option('blogname', $site_name);
        update_option('blogdescription', $tagline);
        update_option(self::OPTION_HOTLINE_1, $hotline_1);
        update_option(self::OPTION_HOTLINE_2, $hotline_2);
        update_option(self::OPTION_ZALO, $zalo_url);

        if ($logo_id && wp_attachment_is_image($logo_id)) {
            set_theme_mod('custom_logo', $logo_id);
        } elseif (!$logo_id) {
            remove_theme_mod('custom_logo');
        }

        $this->redirect_with_notice('settings', 'settings-saved');
    }

    private function render_homepage()
    {
        $front_page_id = (int) get_option('page_on_front');
        $front_page = $front_page_id ? get_post($front_page_id) : null;
        $action = '';
        if ($front_page) {
            $action = sprintf(
                '<a class="button button-primary" href="%s">Mở trình sửa Flatsome</a>',
                esc_url(get_edit_post_link($front_page_id))
            );
        }
        $this->render_page_header(
            'TRANG CHỦ',
            'Thông tin trang chủ',
            'Chỉnh sửa thông tin cơ bản; bố cục Flatsome được giữ nguyên.',
            $action
        );

        if (!$front_page) {
            echo '<div class="notice notice-warning"><p>Website chưa chọn trang chủ tĩnh.</p></div>';
            return;
        }

        $featured_id = (int) get_post_thumbnail_id($front_page_id);
        $featured_url = $featured_id ? wp_get_attachment_image_url($featured_id, 'large') : '';
        ?>
        <div class="tvcms-grid tvcms-grid--two">
            <form class="tvcms-panel tvcms-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <input type="hidden" name="action" value="tvcms_save_homepage">
                <input type="hidden" name="front_page_id" value="<?php echo esc_attr((string) $front_page_id); ?>">
                <?php wp_nonce_field('tvcms_save_homepage_' . $front_page_id); ?>
                <label>
                    <span>Tiêu đề trang</span>
                    <input type="text" name="title" maxlength="200" required value="<?php echo esc_attr(get_the_title($front_page)); ?>">
                </label>
                <label>
                    <span>Mô tả ngắn</span>
                    <textarea name="excerpt" rows="5"><?php echo esc_textarea($front_page->post_excerpt); ?></textarea>
                </label>
                <div class="tvcms-media-field">
                    <span class="tvcms-label">Ảnh đại diện</span>
                    <input class="tvcms-media-id" type="hidden" name="featured_id" value="<?php echo esc_attr((string) $featured_id); ?>">
                    <div class="tvcms-media-preview tvcms-media-preview--wide">
                        <?php if ($featured_url) : ?>
                            <img src="<?php echo esc_url($featured_url); ?>" alt="">
                        <?php else : ?>
                            <span>Chưa chọn ảnh đại diện</span>
                        <?php endif; ?>
                    </div>
                    <div class="tvcms-actions">
                        <button class="button tvcms-media-select" type="button">Chọn ảnh</button>
                        <button class="button tvcms-media-remove" type="button">Bỏ chọn</button>
                    </div>
                </div>
                <button class="button button-primary button-hero" type="submit">Lưu trang chủ</button>
            </form>

            <section class="tvcms-panel tvcms-warning-panel">
                <span class="dashicons dashicons-info-outline"></span>
                <h2>Nội dung đang dùng UX Builder</h2>
                <p>Trang chủ chứa shortcode Flatsome. Để tránh hỏng giao diện, CMS chỉ sửa tiêu đề, mô tả và ảnh đại diện.</p>
                <p>Các banner, khối dịch vụ và bố cục chi tiết tiếp tục sửa bằng UX Builder của Flatsome.</p>
                <a class="button" href="<?php echo esc_url(get_edit_post_link($front_page_id)); ?>">Mở trang chỉnh sửa</a>
            </section>
        </div>
        <?php
    }

    public function save_homepage()
    {
        $this->require_permission();
        $front_page_id = isset($_POST['front_page_id']) ? absint($_POST['front_page_id']) : 0;
        check_admin_referer('tvcms_save_homepage_' . $front_page_id);

        if (!$front_page_id || $front_page_id !== (int) get_option('page_on_front')) {
            $this->redirect_with_notice('homepage', 'invalid-request');
        }

        $title = isset($_POST['title'])
            ? sanitize_text_field(wp_unslash($_POST['title']))
            : '';
        $excerpt = isset($_POST['excerpt'])
            ? sanitize_textarea_field(wp_unslash($_POST['excerpt']))
            : '';
        if ('' === $title) {
            $this->redirect_with_notice('homepage', 'invalid-request');
        }

        $result = wp_update_post(
            array(
                'ID' => $front_page_id,
                'post_title' => $title,
                'post_excerpt' => $excerpt,
            ),
            true
        );
        if (is_wp_error($result)) {
            $this->redirect_with_notice('homepage', 'save-failed');
        }

        $featured_id = isset($_POST['featured_id']) ? absint($_POST['featured_id']) : 0;
        if ($featured_id && wp_attachment_is_image($featured_id)) {
            set_post_thumbnail($front_page_id, $featured_id);
        } elseif (!$featured_id) {
            delete_post_thumbnail($front_page_id);
        }

        $this->redirect_with_notice('homepage', 'homepage-saved');
    }

    private function class_posts()
    {
        return get_posts(
            array(
                'post_type' => 'post',
                'post_status' => array('publish', 'draft', 'pending', 'future'),
                'posts_per_page' => 50,
                's' => 'LỚP MỚI',
                'orderby' => 'date',
                'order' => 'DESC',
            )
        );
    }

    private function render_classes()
    {
        $class_id = isset($_GET['class_id']) ? absint($_GET['class_id']) : 0;
        $editing = $class_id ? get_post($class_id) : null;
        if ($editing && ('post' !== $editing->post_type || !current_user_can('edit_post', $class_id))) {
            $editing = null;
            $class_id = 0;
        }

        $this->render_page_header(
            'LỚP MỚI',
            $editing ? 'Chỉnh sửa lớp' : 'Đăng lớp mới',
            'Lớp được lưu thành bài viết WordPress và xuất hiện trên website.'
        );
        ?>
        <div class="tvcms-grid tvcms-grid--classes">
            <form class="tvcms-panel tvcms-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <input type="hidden" name="action" value="tvcms_save_class">
                <input type="hidden" name="class_id" value="<?php echo esc_attr((string) $class_id); ?>">
                <?php wp_nonce_field('tvcms_save_class_' . $class_id); ?>
                <label>
                    <span>Tiêu đề lớp</span>
                    <input
                        type="text"
                        name="title"
                        maxlength="200"
                        required
                        value="<?php echo esc_attr($editing ? $editing->post_title : 'LỚP MỚI NGÀY ' . wp_date('d/m/Y')); ?>"
                    >
                </label>
                <div>
                    <span class="tvcms-label">Nội dung lớp</span>
                    <?php
                    wp_editor(
                        $editing ? $editing->post_content : '',
                        'tvcms_class_content',
                        array(
                            'textarea_name' => 'content',
                            'textarea_rows' => 12,
                            'media_buttons' => true,
                            'teeny' => false,
                        )
                    );
                    ?>
                </div>
                <label>
                    <span>Trạng thái</span>
                    <select name="post_status">
                        <option value="publish" <?php selected($editing ? $editing->post_status : 'publish', 'publish'); ?>>Đăng ngay</option>
                        <option value="draft" <?php selected($editing ? $editing->post_status : '', 'draft'); ?>>Lưu nháp</option>
                    </select>
                </label>
                <div class="tvcms-actions">
                    <button class="button button-primary button-hero" type="submit">
                        <?php echo esc_html($editing ? 'Cập nhật lớp' : 'Đăng lớp'); ?>
                    </button>
                    <?php if ($editing) : ?>
                        <a class="button" href="<?php echo esc_url($this->admin_url_for('classes')); ?>">Tạo lớp khác</a>
                    <?php endif; ?>
                </div>
            </form>

            <section class="tvcms-panel">
                <div class="tvcms-panel-heading">
                    <div>
                        <span class="dashicons dashicons-list-view"></span>
                        <h2>Lớp gần đây</h2>
                    </div>
                </div>
                <div class="tvcms-class-list">
                    <?php foreach ($this->class_posts() as $class_post) : ?>
                        <article>
                            <div>
                                <strong><?php echo esc_html(get_the_title($class_post)); ?></strong>
                                <small>
                                    <?php echo esc_html(get_the_date('d/m/Y H:i', $class_post)); ?>
                                    · <?php echo esc_html('publish' === $class_post->post_status ? 'Đã đăng' : 'Bản nháp'); ?>
                                </small>
                            </div>
                            <a class="button button-small" href="<?php echo esc_url($this->admin_url_for('classes', array('class_id' => $class_post->ID))); ?>">
                                Sửa
                            </a>
                        </article>
                    <?php endforeach; ?>
                </div>
            </section>
        </div>
        <?php
    }

    public function save_class()
    {
        $this->require_permission();
        $class_id = isset($_POST['class_id']) ? absint($_POST['class_id']) : 0;
        check_admin_referer('tvcms_save_class_' . $class_id);

        if ($class_id && !current_user_can('edit_post', $class_id)) {
            wp_die(esc_html__('Bạn không có quyền sửa bài viết này.', 'tri-viet-cms'));
        }

        $title = isset($_POST['title'])
            ? sanitize_text_field(wp_unslash($_POST['title']))
            : '';
        $content = isset($_POST['content'])
            ? wp_kses_post(wp_unslash($_POST['content']))
            : '';
        $status = isset($_POST['post_status'])
            ? sanitize_key(wp_unslash($_POST['post_status']))
            : 'draft';
        if (!in_array($status, array('publish', 'draft'), true)) {
            $status = 'draft';
        }
        if ('' === $title || '' === trim(wp_strip_all_tags($content))) {
            $this->redirect_with_notice('classes', 'invalid-request');
        }

        $post_data = array(
            'post_type' => 'post',
            'post_title' => $title,
            'post_content' => $content,
            'post_status' => $status,
        );
        if ($class_id) {
            $post_data['ID'] = $class_id;
            $result = wp_update_post($post_data, true);
        } else {
            $result = wp_insert_post($post_data, true);
        }
        if (is_wp_error($result)) {
            $this->redirect_with_notice('classes', 'save-failed');
        }

        $this->redirect_with_notice('classes', 'class-saved', array('class_id' => (int) $result));
    }

    private function get_attachment_ids($option_name, $limit)
    {
        $ids = get_option($option_name, array());
        if (!is_array($ids)) {
            return array();
        }
        $clean = array();
        foreach ($ids as $id) {
            $id = absint($id);
            if ($id && wp_attachment_is_image($id)) {
                $clean[] = $id;
            }
        }
        return array_slice(array_values(array_unique($clean)), 0, $limit);
    }

    private function render_feedback_group($title, $description, $name, $ids, $slots)
    {
        ?>
        <section class="tvcms-panel">
            <div class="tvcms-panel-heading tvcms-panel-heading--stack">
                <div>
                    <span class="dashicons dashicons-format-gallery"></span>
                    <h2><?php echo esc_html($title); ?></h2>
                </div>
                <p><?php echo esc_html($description); ?></p>
            </div>
            <div class="tvcms-feedback-grid">
                <?php for ($index = 0; $index < $slots; $index++) : ?>
                    <?php
                    $attachment_id = isset($ids[$index]) ? (int) $ids[$index] : 0;
                    $image_url = $attachment_id
                        ? wp_get_attachment_image_url($attachment_id, 'medium')
                        : '';
                    ?>
                    <div class="tvcms-feedback-card tvcms-media-field">
                        <span class="tvcms-feedback-number"><?php echo esc_html((string) ($index + 1)); ?></span>
                        <input
                            class="tvcms-media-id"
                            type="hidden"
                            name="<?php echo esc_attr($name); ?>[]"
                            value="<?php echo esc_attr((string) $attachment_id); ?>"
                        >
                        <div class="tvcms-media-preview">
                            <?php if ($image_url) : ?>
                                <img src="<?php echo esc_url($image_url); ?>" alt="">
                            <?php else : ?>
                                <span>Chưa chọn ảnh</span>
                            <?php endif; ?>
                        </div>
                        <div class="tvcms-actions">
                            <button class="button tvcms-media-select" type="button">Chọn ảnh</button>
                            <button class="button-link-delete tvcms-media-remove" type="button">Bỏ</button>
                        </div>
                    </div>
                <?php endfor; ?>
            </div>
        </section>
        <?php
    }

    private function render_feedback()
    {
        $homepage_ids = $this->get_attachment_ids(self::OPTION_HOMEPAGE_FEEDBACK, 20);
        $shared_ids = $this->get_attachment_ids(self::OPTION_FEEDBACK, 6);
        $this->render_page_header(
            'PHẢN HỒI PHỤ HUYNH',
            'Quản lý thư viện phản hồi',
            'Chọn ảnh trực tiếp từ Media của WordPress.'
        );
        ?>
        <form class="tvcms-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
            <input type="hidden" name="action" value="tvcms_save_feedback">
            <?php wp_nonce_field('tvcms_save_feedback'); ?>
            <?php
            $this->render_feedback_group(
                'Ảnh phản hồi trang chủ',
                'Tối đa 20 ảnh, hiển thị theo đúng thứ tự.',
                'homepage_feedback_ids',
                $homepage_ids,
                20
            );
            $this->render_feedback_group(
                'Ảnh phản hồi dùng chung',
                'Sáu ảnh có thể chèn bằng shortcode [tri_viet_feedback].',
                'feedback_ids',
                $shared_ids,
                6
            );
            ?>
            <section class="tvcms-panel tvcms-feedback-publish">
                <label class="tvcms-checkbox">
                    <input
                        type="checkbox"
                        name="feedback_enabled"
                        value="1"
                        <?php checked(get_option(self::OPTION_FEEDBACK_ENABLED), '1'); ?>
                    >
                    <span>
                        <strong>Tự động thêm thư viện phản hồi vào cuối trang chủ</strong>
                        <small>Chỉ bật sau khi đã chọn và kiểm tra đủ ảnh.</small>
                    </span>
                </label>
                <button class="button button-primary button-hero" type="submit">Lưu phản hồi</button>
            </section>
        </form>
        <?php
    }

    public function save_feedback()
    {
        $this->require_permission();
        check_admin_referer('tvcms_save_feedback');

        $homepage_ids = isset($_POST['homepage_feedback_ids'])
            ? (array) wp_unslash($_POST['homepage_feedback_ids'])
            : array();
        $shared_ids = isset($_POST['feedback_ids'])
            ? (array) wp_unslash($_POST['feedback_ids'])
            : array();

        update_option(
            self::OPTION_HOMEPAGE_FEEDBACK,
            $this->sanitize_attachment_ids($homepage_ids, 20)
        );
        update_option(
            self::OPTION_FEEDBACK,
            $this->sanitize_attachment_ids($shared_ids, 6)
        );
        update_option(
            self::OPTION_FEEDBACK_ENABLED,
            !empty($_POST['feedback_enabled']) ? '1' : '0'
        );

        $this->redirect_with_notice('feedback', 'feedback-saved');
    }

    private function sanitize_attachment_ids($values, $limit)
    {
        $clean = array();
        foreach ((array) $values as $value) {
            $id = absint($value);
            if ($id && wp_attachment_is_image($id)) {
                $clean[] = $id;
            }
        }
        return array_slice(array_values(array_unique($clean)), 0, $limit);
    }

    public function feedback_shortcode($atts)
    {
        $atts = shortcode_atts(
            array('group' => 'shared'),
            $atts,
            'tri_viet_feedback'
        );
        $option = 'homepage' === sanitize_key($atts['group'])
            ? self::OPTION_HOMEPAGE_FEEDBACK
            : self::OPTION_FEEDBACK;
        $limit = self::OPTION_HOMEPAGE_FEEDBACK === $option ? 20 : 6;
        $ids = $this->get_attachment_ids($option, $limit);
        if (!$ids) {
            return '';
        }

        static $style_printed = false;
        $html = '';
        if (!$style_printed) {
            $style_printed = true;
            $html .= '<style>.tvcms-public-feedback{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:28px auto;max-width:1180px}.tvcms-public-feedback a{display:block;overflow:hidden;border-radius:14px;background:#fff;box-shadow:0 8px 24px rgba(14,73,50,.14)}.tvcms-public-feedback img{display:block;width:100%;height:auto}.tvcms-public-feedback__title{grid-column:1/-1;text-align:center;color:#087849}@media(max-width:700px){.tvcms-public-feedback{grid-template-columns:1fr 1fr;gap:12px}}</style>';
        }
        $html .= '<section class="tvcms-public-feedback" aria-label="Phản hồi phụ huynh">';
        $html .= '<h2 class="tvcms-public-feedback__title">Phản hồi từ phụ huynh</h2>';
        foreach ($ids as $id) {
            $full = wp_get_attachment_image_url($id, 'full');
            if (!$full) {
                continue;
            }
            $html .= '<a href="' . esc_url($full) . '" target="_blank" rel="noopener">';
            $html .= wp_get_attachment_image(
                $id,
                'large',
                false,
                array('loading' => 'lazy')
            );
            $html .= '</a>';
        }
        $html .= '</section>';
        return $html;
    }

    public function maybe_append_homepage_feedback($content)
    {
        static $appended = false;
        if (
            $appended ||
            is_admin() ||
            !is_front_page() ||
            !in_the_loop() ||
            !is_main_query() ||
            '1' !== get_option(self::OPTION_FEEDBACK_ENABLED)
        ) {
            return $content;
        }
        $appended = true;
        return $content . $this->feedback_shortcode(array('group' => 'homepage'));
    }

    private function render_pages()
    {
        $pages = get_pages(
            array(
                'sort_column' => 'post_title',
                'sort_order' => 'ASC',
                'post_status' => array('publish', 'draft', 'private', 'pending'),
            )
        );
        $action = sprintf(
            '<a class="button button-primary" href="%s">Thêm trang mới</a>',
            esc_url(admin_url('post-new.php?post_type=page'))
        );
        $this->render_page_header(
            'TRANG NỘI DUNG',
            'Quản lý các trang',
            'Mở trang bằng trình sửa WordPress hoặc UX Builder.',
            $action
        );
        ?>
        <section class="tvcms-panel tvcms-table-panel">
            <table class="widefat striped">
                <thead>
                    <tr>
                        <th>Tiêu đề</th>
                        <th>Trạng thái</th>
                        <th>Cập nhật</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($pages as $page) : ?>
                        <tr>
                            <td>
                                <strong><?php echo esc_html(get_the_title($page)); ?></strong>
                                <?php if ((int) get_option('page_on_front') === (int) $page->ID) : ?>
                                    <span class="tvcms-pill">Trang chủ</span>
                                <?php endif; ?>
                            </td>
                            <td><?php echo esc_html(get_post_status_object($page->post_status)->label); ?></td>
                            <td><?php echo esc_html(get_the_modified_date('d/m/Y H:i', $page)); ?></td>
                            <td class="tvcms-table-actions">
                                <a class="button button-small" href="<?php echo esc_url(get_edit_post_link($page->ID)); ?>">Sửa</a>
                                <?php if ('publish' === $page->post_status) : ?>
                                    <a class="button button-small" href="<?php echo esc_url(get_permalink($page)); ?>" target="_blank" rel="noopener">Xem</a>
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </section>
        <?php
    }

    private function render_media()
    {
        $media = get_posts(
            array(
                'post_type' => 'attachment',
                'post_mime_type' => 'image',
                'post_status' => 'inherit',
                'posts_per_page' => 30,
                'orderby' => 'date',
                'order' => 'DESC',
            )
        );
        $action = sprintf(
            '<a class="button button-primary" href="%s">Tải ảnh mới</a>',
            esc_url(admin_url('media-new.php'))
        );
        $this->render_page_header(
            'THƯ VIỆN ẢNH',
            'Ảnh mới tải lên',
            'Ảnh được quản lý trực tiếp bằng Media của WordPress.',
            $action
        );
        ?>
        <section class="tvcms-panel">
            <div class="tvcms-media-grid">
                <?php foreach ($media as $attachment) : ?>
                    <?php $thumb = wp_get_attachment_image_url($attachment->ID, 'medium'); ?>
                    <?php if (!$thumb) continue; ?>
                    <a href="<?php echo esc_url(get_edit_post_link($attachment->ID)); ?>">
                        <img src="<?php echo esc_url($thumb); ?>" alt="">
                        <span><?php echo esc_html(get_the_title($attachment)); ?></span>
                    </a>
                <?php endforeach; ?>
            </div>
            <div class="tvcms-actions tvcms-actions--footer">
                <a class="button" href="<?php echo esc_url(admin_url('upload.php')); ?>">Mở toàn bộ Media</a>
            </div>
        </section>
        <?php
    }
}

register_activation_hook(__FILE__, array('Tri_Viet_CMS', 'activate'));
Tri_Viet_CMS::instance();
