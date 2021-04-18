from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters
from telegram.utils.helpers import mention_markdown, escape_markdown

from YARBot import dispatcher
from YARBot.modules.disable import DisableAbleCommandHandler
from YARBot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply


@user_admin
def start_attendance(update, context):
    if ('flag' in context.chat_data) and (context.chat_data['flag'] == 1):
        update.message.reply_text(
            "Please close the current attendance first",
        )
    elif ('flag' not in context.chat_data) or (context.chat_data['flag'] == 0):
        context.chat_data['flag'] = 1
        context.chat_data['attendees'] = {}
        context.chat_data['id'] = update.effective_chat.id
        keyboard = [
            [
                InlineKeyboardButton(
                    "Present",
                    callback_data='present',
                ),
            ],
            [
                InlineKeyboardButton(
                    "End Attendance (Admin only)",
                    callback_data='end_attendance',
                ),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.chat_data['message'] = update.message.reply_text(
            "Please mark your attendance", reply_markup=reply_markup,
        )


def mark_attendance(update, context):
    query = update.callback_query
    if (
        str(update.effective_user.id) not in
        context.chat_data['attendees'].keys()
    ):
        context.chat_data['attendees'][
                update.effective_user.id
        ] = f'{escape_markdown(update.effective_user.full_name)}'
        context.bot.answer_callback_query(
            callback_query_id=query.id,
            text="Your attendance has been marked",
            show_alert=True,
        )
    else:
        context.bot.answer_callback_query(
            callback_query_id=query.id,
            text="Your attendance is already marked",
            show_alert=True,
        )
    query.answer()


@user_admin_no_reply
def end_attendance(update, context):
    query = update.callback_query
    query.answer()
    if (context.chat_data['id'] != update.effective_chat.id):
        return
    attendee_list = "\n- ".join([
        mention_markdown(id, name)
            for id, name in context.chat_data['attendees'].items()
    ])
    context.bot.edit_message_text(
        text="Attendance is over. " +
        str(len(context.chat_data['attendees'])) +
        " member(s) marked attendance.\n" +
        "Here is the list:\n- " + attendee_list,
        chat_id=context.chat_data['message'].chat_id,
        message_id=context.chat_data['message'].message_id,
        parse_mode=ParseMode.MARKDOWN,
    )
    context.chat_data['flag'] = 0
    context.chat_data['attendees'].clear()


__help__ = """
- `/attendance`*:* Start the attendance
"""

START_ATTENDANCE = DisableAbleCommandHandler("attendance", start_attendance)
MARK_ATTENDANCE = CallbackQueryHandler(mark_attendance, pattern="present")
END_ATTENDANCE = CallbackQueryHandler(end_attendance, pattern="end_attendance")

dispatcher.add_handler(START_ATTENDANCE)
dispatcher.add_handler(MARK_ATTENDANCE)
dispatcher.add_handler(END_ATTENDANCE)

__mod_name__ = "Attendance"
__command_list__ = ["attendance"]
__handlers__ = [START_ATTENDANCE, END_ATTENDANCE]