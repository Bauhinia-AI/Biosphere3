/******************************************************************************************
 * Name: UIClock.cs
 * Created by: Jeremy Voss
 * Created on: 02/20/2019
 * Last Modified: 02/20/2019
 * Description:
 * The UI Clock is responsible for managing the date/time system.  It utilizes an
 * event driven system to notify the rest of our game of time related events.
 ******************************************************************************************/
using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    public class UIClock : MonoBehaviour
    {
        #region Events

        public delegate void ClockEvent(UIClock clock);
        /// <summary>
        /// Called every tick of the clock (once the timescale value is met by time).
        /// </summary>
        public static event ClockEvent Tick;

        #endregion

        #region Fields & Properties

        public enum CalendarMonths { January = 0, February = 1, March = 2, April = 3, May = 4, June = 5, July = 6, August = 7, September = 8, October = 9, November = 10, December = 11 }

        [SerializeField]
        [Range(0.01f, 60.0f)]
        [Tooltip("How fast our clock progresses time. [60 = Real Time]")]
        protected float timeScale = 60f;
        [SerializeField]
        [Tooltip("How many minutes are there in an hour?")]
        protected int minutesPerHour = 60;
        [SerializeField]
        [Tooltip("How many hours are there in a day?")]
        protected int hoursPerDay = 24;
        [SerializeField]
        [Tooltip("How many days are there in a month?")]
        protected int daysPerMonth = 31;
        [SerializeField]
        [Tooltip("How many months are there in a year?")]
        protected int monthsPerYear = System.Enum.GetValues(typeof(CalendarMonths)).Length;
        [SerializeField]
        [Tooltip("When we reset minutes, where do we start counting from?")]
        protected int resetMinute = 0;
        [SerializeField]
        [Tooltip("When we reset hours, where do we start counting from?")]
        protected int resetHour = 0;
        [SerializeField]
        [Tooltip("When we reset days, where do we start counting from?")]
        protected int resetDay = 1;
        [SerializeField]
        [Tooltip("When we reset months, where do we start counting from?")]
        protected int resetMonth = 0;
        [SerializeField]
        [Tooltip("Should the clock start paused?")]
        protected bool startPaused = false;

        /// <summary>
        /// Tells us if the clock should currently be paused.
        /// </summary>
        protected bool isPaused = false;
        /// <summary>
        /// The time variable is used to track time passing.
        /// </summary>
        protected float time = 0f;
        /// <summary>
        /// The current minute/hour/day/month/year variables keep track of what our current date/time is.
        /// </summary>
        protected int currentMinute, currentHour, currentDay, currentMonth, currentYear;

        /// <summary>
        /// Gets the current time formatted as a string.
        /// </summary>
        public virtual string GetTimeString { get { return currentHour.ToString("00") + ":" + currentMinute.ToString("00"); } }
        /// <summary>
        /// Gets the current date formatted as a string.
        /// </summary>
        public virtual string GetDateString { get { return GetMonthString + " " + currentDay.ToString() + " Year " + currentYear; } }
        /// <summary>
        /// Gets the current date/time formatted as a string.
        /// </summary>
        public virtual string GetDateTimeString { get { return GetTimeString + " " + GetDateString; } }
        /// <summary>
        /// Gets the current minute.
        /// </summary>
        public virtual int GetMinute { get { return currentMinute; } }
        /// <summary>
        /// Gets the current hour.
        /// </summary>
        public virtual int GetHour { get { return currentHour; } }
        /// <summary>
        /// Gets the current day.
        /// </summary>
        public virtual int GetDay { get { return currentDay; } }
        /// <summary>
        /// Gets the current month.
        /// </summary>
        public virtual int GetMonth { get { return currentMonth; } }
        /// <summary>
        /// Gets the current month as a calendar month string.
        /// </summary>
        public virtual string GetMonthString { get { return ((CalendarMonths)currentMonth).ToString(); } }
        /// <summary>
        /// Gets the current year.
        /// </summary>
        public virtual int GetYear { get { return currentYear; } }

        #endregion

        #region Monobehavior Callbacks

        protected virtual void Awake()
        {
            Tick += UIClock_Tick;
        }

        protected virtual void Start()
        {
            if (startPaused)
            {
                isPaused = true;
            }
        }

        protected virtual void OnDestroy()
        {
            Tick -= UIClock_Tick;
        }

        protected virtual void Update()
        {
            if (!isPaused)
            {
                time += Time.deltaTime;
                if (time >= timeScale)
                {
                    if (Tick != null)
                    {
                        Tick(this);
                    }
                }
            }
        }

        #endregion

        #region Callbacks

        /// <summary>
        /// This gets called when the Tick event is raised.
        /// </summary>
        /// <param name="clock">The instance of the clock calling the tick event.</param>
        protected void UIClock_Tick(UIClock clock)
        {
            UpdateTime();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Pauses the clock.
        /// </summary>
        public virtual void Pause()
        {
            isPaused = true;
        }

        /// <summary>
        /// Unpauses the clock.
        /// </summary>
        public virtual void Unpause()
        {
            isPaused = false;
        }

        /// <summary>
        /// Used to set the current time.
        /// </summary>
        /// <param name="hour">The current hour.</param>
        /// <param name="minute">The current minute.</param>
        public virtual void SetTime(int hour, int minute)
        {
            currentHour = hour;
            currentMinute = minute;
        }

        /// <summary>
        /// Used to set the current date.
        /// </summary>
        /// <param name="day">The current day.</param>
        /// <param name="month">The current month.</param>
        /// <param name="year">The current year.</param>
        public virtual void SetDate(int day, int month, int year)
        {
            currentDay = day;
            if (month >= System.Enum.GetValues(typeof(CalendarMonths)).Length)
            {
                month = (int)CalendarMonths.December;
            }
            else if (month < 0)
            {
                month = (int)CalendarMonths.January;
            }
            currentMonth = month;
            currentYear = year;
        }

        /// <summary>
        /// Used to set the current date/time.
        /// </summary>
        /// <param name="hour">The current hour.</param>
        /// <param name="minute">The current minute.</param>
        /// <param name="day">The current day.</param>
        /// <param name="month">The current month.</param>
        /// <param name="year">The current year.</param>
        public virtual void SetDateTime(int hour, int minute, int day, int month, int year)
        {
            SetTime(hour, minute);
            SetDate(day, month, year);
        }

        #endregion

        #region Protected Methods

        /// <summary>
        /// Updates the current time.
        /// </summary>
        protected virtual void UpdateTime()
        {
            time = 0f;
            UpdateMinute();
        }

        /// <summary>
        /// Updates the current minute.
        /// </summary>
        protected virtual void UpdateMinute()
        {
            currentMinute++;

            if (currentMinute >= minutesPerHour)
            {
                currentMinute = resetMinute;
                UpdateHour();
            }
        }

        /// <summary>
        /// Updates the current hour.
        /// </summary>
        protected virtual void UpdateHour()
        {
            currentHour++;

            if(currentHour >= hoursPerDay)
            {
                currentHour = resetHour;
                UpdateDay();
            }
        }

        /// <summary>
        /// Updates the current day.
        /// </summary>
        protected virtual void UpdateDay()
        {
            currentDay++;

            if(currentDay > daysPerMonth)
            {
                currentDay = resetDay;
                UpdateMonth();
            }
        }

        /// <summary>
        /// Updates the current month.
        /// </summary>
        protected virtual void UpdateMonth()
        {
            currentMonth++;
            
            if(currentMonth >= System.Enum.GetValues(typeof(CalendarMonths)).Length)
            {
                currentMonth = resetMonth;
                UpdateYear();
            }
        }

        /// <summary>
        /// Updates the current year.
        /// </summary>
        protected virtual void UpdateYear()
        {
            currentYear++;
        }

        #endregion
    }
}