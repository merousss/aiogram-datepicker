from datetime import datetime, timedelta
import calendar
import locale as lc
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData, CallbackQuery

class DpCallback(CallbackData, prefix='datepicker'):
  action: Optional[str] = None
  date: Optional[str] = None
  month: Optional[int] = None
  year: Optional[int] = None
  weekday: Optional[int] = None
  day: Optional[int] = None
  selected_date: Optional[str] = None

class DatePicker:

  def __init__(
      self,
      placeholder:str ="📆 Selected date: ",
      oneTap:bool = False,
      locale = 'en_US',
      firstweekday = 0,
      controlButtons=["<<", ">>"],
      blockedDays = [],
      blockedButton:str = '❌',
      emptyButton:str = 'ㅤ',
      dateFormat:str = "%d.%m.%Y",
      yearRange=120,
      confirmButton: str = 'Confirm ✅',
      selectionFormat:Optional[str] = '∙{}∙',
      predefined:Optional[datetime] = None,
  ):
    self.placeholder = placeholder
    self.oneTap = oneTap
    self.locale = locale
    self.firstweekday= firstweekday
    self.controlButtons = controlButtons
    self.blockedDays = blockedDays
    self.blockedButton = blockedButton
    self.dateFormat = dateFormat
    self.yearRange = abs(yearRange)
    self.emptyButton = emptyButton
    self.confirmButton = confirmButton
    self.selectionFormat = selectionFormat
    self.predefined = predefined


  async def start_calendar(
      self,
      year = datetime.now().year,
      month = datetime.now().month,
      context = 'datepicker',
      selected_date = None
  ):
    
    lc.setlocale(lc.LC_ALL, self.locale)
    calendar.setfirstweekday(self.firstweekday)

    if not selected_date and self.predefined:
      selected_date = datetime.strftime(self.predefined, self.dateFormat)
      year=self.predefined.year
      month=self.predefined.month

    cal = calendar.monthcalendar(year, month)

    
    def _build_datepicker():
      builder = InlineKeyboardBuilder()

      weekday = calendar.day_abbr[self.firstweekday:] + calendar.day_abbr[:self.firstweekday]  

      builder.row(
        InlineKeyboardButton(
          text=self.controlButtons[0],
          callback_data=DpCallback(action="prev_m", month=month, year=year, selected_date=selected_date).pack()
        ),
        InlineKeyboardButton(
          text=f"{calendar.month_abbr[month].capitalize()} • {year:04}",
          callback_data=DpCallback(action="change_month", month=month, year=year, selected_date=selected_date).pack()
        ),
        InlineKeyboardButton(
          text=self.controlButtons[1],
          callback_data=DpCallback(action="next_m", month=month, year=year, selected_date=selected_date).pack()
        ),
      )

      for day in range(len(weekday)):
        builder.add(InlineKeyboardButton(
          text=f"{weekday[day]}",
          callback_data=DpCallback(action="weekday", month=month, year=year, weekday=day).pack()
        ))

      ##building calendar
      for week in cal:
        for day in week:
          action = "select"
          text=f"{day}"
          day_num=day

          if day == 0:
            action = "ignore"
            text = self.emptyButton
            day_num=None
          elif datetime(year, month, day).date() in self.blockedDays:
            action = "blocked"
            text = self.blockedButton

          date = datetime.strftime(datetime(year, month, day), self.dateFormat) if action != "ignore" else None
          
          if self.selectionFormat and date == selected_date and day != 0:
            text=self.selectionFormat.format(day)

          builder.button(
            text=text,
            callback_data=DpCallback(action=action, date=date, year=year, month=month, day=day_num, selected_date=date),
          )

      builder.adjust(3, 7)

      if self.oneTap == False:
        builder.row(
          InlineKeyboardButton(
            text=self.confirmButton,
            callback_data=DpCallback(action="ok", month=month, year=year, date=selected_date).pack()
          )
        )

      return builder.as_markup(resize_keyboard=True)


    def _build_monthpicker():
      builder = InlineKeyboardBuilder()
      builder.row(
        InlineKeyboardButton(
          text=self.controlButtons[0],
          callback_data=DpCallback(action="prev_y", month=month, year=year, selected_date=selected_date).pack()
        ),
        InlineKeyboardButton(
          text=f"{year}",
          callback_data=DpCallback(action="change_year", month=month, year=year, selected_date=selected_date).pack()
        ),
        InlineKeyboardButton(
          text=self.controlButtons[1],
          callback_data=DpCallback(action="next_y", month=month, year=year, selected_date=selected_date).pack()
        ))
      
      for i in range(1,13):
        text=calendar.month_abbr[i].capitalize()

        if selected_date:
          selected_month=datetime.strptime(selected_date, self.dateFormat).month
          selected_year=datetime.strptime(selected_date, self.dateFormat).year
          if self.selectionFormat and selected_month == i and selected_year == year:
            text=self.selectionFormat.format(text)

        builder.button(
          text=text,
          callback_data=DpCallback(action="select_month", month=i, year=year, selected_date=selected_date).pack()
        )
      
      builder.adjust(3,4)
      return builder.as_markup()


    def _build_yearpicker():
      builder = InlineKeyboardBuilder()
      start_year = int(f"{year:04}"[:3]+"0")
      end_year = int(f"{year:04}"[:3]+"9")
      builder.row(
        InlineKeyboardButton(
          text=self.controlButtons[0],
          callback_data=DpCallback(action="prev_decade", month=month, year=year, selected_date=selected_date).pack()
        ),
        InlineKeyboardButton(
          text=f"{start_year}-{end_year}",
          callback_data=DpCallback(action="ignore", month=month, year=year, selected_date=selected_date).pack()
        ),
        InlineKeyboardButton(
          text=self.controlButtons[1],
          callback_data=DpCallback(action="next_decade", month=month, year=year, selected_date=selected_date).pack()
        ))
      
      if not calendar.isleap(start_year):
        start_year+=start_year%4

      year_list=list(range(start_year-3, start_year+13))

      
      for _year in year_list:
        text=self.emptyButton
        action="ignore"
        if (_year <= datetime.now().year+self.yearRange 
              and 
            _year >= datetime.now().year-self.yearRange
        ):
          text=f"{_year}"
          action="select_year"
          if selected_date:
            selected_year=datetime.strptime(selected_date, self.dateFormat).year
            if self.selectionFormat and selected_year == _year:
              text=self.selectionFormat.format(text)
        builder.button(
          text=text,
          callback_data=DpCallback(action=action, month=month, year=_year, selected_date=selected_date)
        )

      builder.adjust(3,4)
      return builder.as_markup()
      
    match context:
      case "monthpicker":
        return _build_monthpicker()
      case "yearpicker":
        return _build_yearpicker()
      case _:
        return _build_datepicker()
        

  async def process_selection(
      self,
      callback: CallbackQuery,
      callback_data: DpCallback
  ):
    date = None
    result = None

    if callback_data.action == "select":
      date = callback_data.date
      if self.oneTap == False:
        try:
          await callback.message.edit_text(
            self.placeholder + date, 
            reply_markup=await self.start_calendar(
              year=callback_data.year, 
              month=callback_data.month, 
              selected_date=date
          ))
        except:
          pass
      else:
        result = date

    if callback_data.action == "select_month":
      await callback.message.edit_reply_markup(
        reply_markup=await self.start_calendar(
          year=callback_data.year, 
          month=callback_data.month, 
          context="datepicker",
          selected_date=callback_data.selected_date
      
      ))

    if callback_data.action == "select_year":
      await callback.message.edit_reply_markup(
        reply_markup=await self.start_calendar(
          year=callback_data.year, 
          month=callback_data.month, 
          context="monthpicker",
          selected_date=callback_data.selected_date
      ))


    if callback_data.action == "next_m":
      new_date = datetime(callback_data.year, callback_data.month, 1) + timedelta(days=31)
      await callback.message.edit_reply_markup(
        reply_markup=await self.start_calendar(
          year=min(new_date.year, datetime.now().year+self.yearRange), 
          month=new_date.month, 
          selected_date=callback_data.selected_date
      ))


    if callback_data.action == "prev_m":
      new_date = datetime(callback_data.year, callback_data.month, 1) - timedelta(days=1)
      await callback.message.edit_reply_markup(
        reply_markup=await self.start_calendar(
          year=max(new_date.year, datetime.now().year-self.yearRange), 
          month=new_date.month, 
          selected_date=callback_data.selected_date
      ))
    
    if callback_data.action == "next_y":
      next_year = min(callback_data.year+1, datetime.now().year+self.yearRange)
      try:
        await callback.message.edit_reply_markup(
          reply_markup=await self.start_calendar(
            year=next_year, 
            month=callback_data.month, 
            context="monthpicker",
            selected_date=callback_data.selected_date
        ))
      except:
        pass


    if callback_data.action == "prev_y":
      prev_year = max(callback_data.year-1, datetime.now().year-self.yearRange)
      try:
        await callback.message.edit_reply_markup(
          reply_markup=await self.start_calendar(
            year=prev_year, 
            month=callback_data.month, 
            context="monthpicker",
            selected_date=callback_data.selected_date
        ))
      except:
        pass

    if callback_data.action == "next_decade":
      next_year = min(callback_data.year+10, datetime.now().year+self.yearRange)
      try:
        await callback.message.edit_reply_markup(
          reply_markup=await self.start_calendar(
            year=next_year, 
            month=callback_data.month, 
            context="yearpicker",
            selected_date=callback_data.selected_date
        ))
      except:
        pass


    if callback_data.action == "prev_decade":
      prev_year = max(callback_data.year-10, datetime.now().year-self.yearRange)
      try:
        await callback.message.edit_reply_markup(
          reply_markup=await self.start_calendar(
            year=prev_year, 
            month=callback_data.month, 
            context="yearpicker",
            selected_date=callback_data.selected_date
        ))
      except:
        pass
    

    if callback_data.action == "change_month":
      await callback.message.edit_reply_markup(
        reply_markup=await self.start_calendar(
          year=callback_data.year, 
          month=callback_data.month, 
          context="monthpicker",
          selected_date=callback_data.selected_date
      ))
    

    if callback_data.action == "change_year":
      await callback.message.edit_reply_markup(
        reply_markup=await self.start_calendar(
          year=callback_data.year, 
          month=callback_data.month, 
          context="yearpicker",
          selected_date=callback_data.selected_date
      ))
    
    await callback.answer()

    if callback_data.action == "ok":
      result = callback_data.date

    return result
