/******************************************************************************************
 * Name: SwatchHandler.cs
 * Created by: Jeremy Voss
 * Created on: 9/12/2018
 * Last Modified: 1/16/2019
 * Description:
 * A simple demo script used to demonstrate how Pixel UI is set up to change color easily
 * via a material.  It also demonstrates how the UI appears in various colors.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    public class SwatchHandler : MonoBehaviour
    {
        #region Public Fields & Properties

        [SerializeField]
        [Tooltip("The image material we will use to demonstrate color changing.")]
        Material imageMaterial = null;

        [SerializeField]
        [Tooltip("The text material we will use to demonstrate color changing.")]
        Material textMaterial = null;

        #endregion

        #region MonoBehaviour Callbacks

        /// <summary>
        /// If we do not change the default color of the material back to white then when we stop our play tests
        /// it will not revert to it's normal color and stay the color we set it to.
        /// </summary>
        private void OnDestroy()
        {
            imageMaterial.color = Color.white;
            textMaterial.color = Color.white;
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// We take the color of the passed image and use that color to change our material color
        /// for demonstration.
        /// </summary>
        public void ChangeColors(Color imageColor, Color textColor)
        {
            imageMaterial.color = imageColor;
            textMaterial.color = textColor;
        }

        #endregion
    }
}