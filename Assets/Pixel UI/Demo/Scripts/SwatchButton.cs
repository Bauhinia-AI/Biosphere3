using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Image))]
    public class SwatchButton : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("The image and text colors to use if clicked.")]
        Color imageColor, textColor = Color.white;
        [SerializeField]
        [Tooltip("Is this button our default swatch button?")]
        bool defaultSwatch = false;

        /// <summary>
        /// The image we will be targeting with this script.
        /// </summary>
        Image image = null;

        #endregion

        #region Monobehavior Callbacks

        private void Awake()
        {
            image = GetComponent<Image>();
        }

        // Use this for initialization
        void Start()
        {
            image.color = imageColor;

            if (defaultSwatch)
                ChangeColors();
        }

        #endregion

        #region Callbacks

        /// <summary>
        /// Called when the button is clicked and tells the swatch handler to change its material colors.
        /// </summary>
        public void ChangeColors()
        {
            GetComponentInParent<SwatchHandler>().ChangeColors(imageColor, textColor);
        }

        #endregion
    }
}