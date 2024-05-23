/******************************************************************************************
 * Name: Range.cs
 * Created by: Jeremy Voss
 * Created on: 02/20/2019
 * Last Modified: 02/27/2019
 * Description:
 * A special value type used for establishing number ranges of type int and float.
 ******************************************************************************************/
namespace PixelsoftGames.PixelUI
{
    [System.Obsolete("This method is now obsolete.  Please use UnityEngine.RangeInt instead.")]
    public struct RangeInt
    {
        #region Fields & Properties

        /// <summary>
        /// The minimum value in the range.
        /// </summary>
        public int Min { get; set; }
        /// <summary>
        /// The maximum value in the range.
        /// </summary>
        public int Max { get; set; }

        #endregion

        #region Constructors

        /// <summary>
        /// Default constructor for the RangeInt class.
        /// </summary>
        /// <param name="min">The minimum value in the range.</param>
        /// <param name="max">The maximum value in the range.</param>
        public RangeInt(int min, int max)
        {
            Min = min;
            Max = max;
        }

        #endregion

        #region Static Methods

        /// <summary>
        /// Returns a range of zero to zero.
        /// </summary>
        public static RangeInt Zero { get { return new RangeInt(0, 0); } }

        #endregion

        #region Public Methods

        /// <summary>
        /// Returns the range formatted as a string.
        /// </summary>
        /// <returns></returns>
        public override string ToString()
        {
            return "(" + Min + " - " + Max + ")";
        }

        /// <summary>
        /// Returns if a value falls within this range.
        /// </summary>
        /// <param name="value">The value being assessed.</param>
        /// <returns></returns>
        public bool IsInRange(int value)
        {
            if (value >= Min && value <= Max)
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        #endregion
    }

    public struct Range
    {
        #region Fields & Properties

        /// <summary>
        /// The minimum value in the range.
        /// </summary>
        public float Min { get; set; }
        /// <summary>
        /// The maximum value in the range.
        /// </summary>
        public float Max { get; set; }

        #endregion

        #region Constructors

        /// <summary>
        /// Default constructor for the Range class.
        /// </summary>
        /// <param name="min">The minimum value in the range.</param>
        /// <param name="max">The maximum value in the range.</param>
        public Range(int min, int max)
        {
            Min = min;
            Max = max;
        }

        #endregion

        #region Static Methods

        /// <summary>
        /// Returns a range from zero to zero.
        /// </summary>
        public static Range Zero { get { return new Range(0, 0); } }

        #endregion

        #region Public Methods

        /// <summary>
        /// Returns the range formatted as a string.
        /// </summary>
        /// <returns></returns>
        public override string ToString()
        {
            return "(" + Min + " - " + Max + ")";
        }

        /// <summary>
        /// Returns if a value falls within this range.
        /// </summary>
        /// <param name="value">The value being assessed.</param>
        /// <returns></returns>
        public bool IsInRange(float value)
        {
            if (value >= Min && value <= Max)
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        #endregion
    }
}