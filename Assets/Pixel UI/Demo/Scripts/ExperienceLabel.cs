/******************************************************************************************
 * Name: ExperienceLabel.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * A simple script that is used to visualize player level in the demo.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Text))]
    public class ExperienceLabel : MonoBehaviour
    {
        #region Fields & Properties

        const string levelString = "Level: ";
        Text label = null;

        #endregion

        #region Monobehaviour Callbacks

        private void Awake()
        {
            UIExperienceBar.LevelUp += On_LevelUp;
        }

        private void Start()
        {
            label = GetComponent<Text>();
            label.text = levelString + 1;
        }

        private void OnDestroy()
        {
            UIExperienceBar.LevelUp -= On_LevelUp;
        }

        #endregion

        #region Callbacks

        /// <summary>
        /// Gets called when the the experience bar has 'leveled up'.
        /// </summary>
        /// <param name="expBar">The exp bar that has leveled up</param>
        private void On_LevelUp(UIExperienceBar expBar)
        {
            label.text = levelString + expBar.GetCurrentLevel;
        }

        #endregion
    }
}