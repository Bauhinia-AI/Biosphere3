/******************************************************************************************
 * Name: UIStatBar.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * A simple script on the Health, Magic, and Energy bars that will take the current
 * value and maximum value and translate it into a slider value ranging 0 to 1. So if my
 * character takes damage I can do my damage calculations for to calculate my new player
 * health.  Then call the SetValue method of this script and pass in my current health and
 * maximum health and it will update the slider accordingly.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Slider))]
    public class UIStatBar : MonoBehaviour
    {
        #region Fields & Properties

        private Slider slider = null;

        #endregion

        #region Monobehaviour Callbacks

        private void Awake()
        {
            slider = GetComponent<Slider>();
        }

        #endregion

        #region public Methods

        /// <summary>
        /// Sets the status bar based on the current, and maximum values (i.e - current health, maximum health)
        /// </summary>
        /// <param name="cur">The current stat value</param>
        /// <param name="max">The maximum stat value</param>
        public void SetValue(int cur, int max)
        {
            slider.value = cur / max;
        }

        #endregion
    }
}
