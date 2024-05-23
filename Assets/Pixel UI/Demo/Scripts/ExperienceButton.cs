/******************************************************************************************
 * Name: ExperienceButton.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * A demo script that grants a certain amount of experience when the user clicks the
 * grant exp button.
 ******************************************************************************************/
using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    public class ExperienceButton : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("The exp bar we will be giving experience points to.")]
        UIExperienceBar expBar;
        [SerializeField]
        [Tooltip("The amount of exp to grant per click.")]
        int expToGrant = 100;

        #endregion

        #region Callbacks

        /// <summary>
        /// Gets called when the button is clicked and grants exp to the exp bar.
        /// </summary>
        public void On_Click()
        {
            expBar.GiveExperiencePoints(expToGrant);
        }

        #endregion
    }
}