use qt_widgets::qt_core::{QBox, QString};
use qt_widgets::{QApplication, QPushButton, QWidget};
// use qt_widgets::qt_core::slots::SlotNoArgs;
use std::rc::Rc;

fn main() {
    let app = QApplication::init(|app| {
        unsafe {
            // initialization goes here
            let widget = QWidget::new_0a();
            widget.resize_2a(320, 240);
            widget.set_window_title(&QString::from_std_str("Hello Qt from Rust!"));
        
            widget.show();
            QApplication::exec()
        }
    });
}
