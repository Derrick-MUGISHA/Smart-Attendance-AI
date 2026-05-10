from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_course_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Fundamental", callback_data="course_fundamental"),
        ],
        [
            InlineKeyboardButton("Frontend", callback_data="course_frontend"),
            InlineKeyboardButton("Backend", callback_data="course_backend"),
        ],
        [
            InlineKeyboardButton("Adv. Frontend", callback_data="course_adv_frontend"),
            InlineKeyboardButton("Adv. Backend", callback_data="course_adv_backend"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_level_keyboard():
    # Keep it for backward compatibility or remove if not needed. 
    # Since we merged level into course for some, maybe we still want it for Fundamental?
    # User said: "foundamental backend and frontend and the adevernsed backend and forontend"
    # Let's simplify and just use the course keyboard for everything if possible.
    keyboard = [
        [
            InlineKeyboardButton("Standard", callback_data="level_standard"),
            InlineKeyboardButton("Advanced", callback_data="level_advanced"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_attendance_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_all"),
            InlineKeyboardButton("📝 Edit", callback_data="edit_attendance"),
            InlineKeyboardButton("❌ Reject", callback_data="reject_attendance"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
