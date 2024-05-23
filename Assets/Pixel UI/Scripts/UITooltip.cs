/******************************************************************************************
 * Name: UITooltip.cs
 * Created by: Jeremy Voss
 * Created on: 02/20/2019
 * Last Modified: 02/27/2019
 * Description:
 * Used to display tooltips while the cursor is hovered over an object.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    public class UITooltip : Singleton<UITooltip>
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("The text being displayed by this tooltip.")]
        private Text tooltip = null;

        #endregion

        #region Monobehavior Callbacks

        private void OnEnable()
        {
            transform.position = Input.mousePosition;
            if (Input.mousePosition.x > Screen.width / 2)
                GetComponent<RectTransform>().pivot = new Vector2(1f, 0.5f);
            else
                GetComponent<RectTransform>().pivot = new Vector2(0f, 0.5f);
        }

        // Update is called once per frame
        private void Update()
        {
            transform.position = Input.mousePosition;
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Sets the text for the tooltip.
        /// </summary>
        /// <param name="text">The text to be displayed.</param>
        public void SetText(string text)
        {
            if (tooltip != null)
                tooltip.text = text;
        }

        /// <summary>
        /// Convenience method for showing the tooltip.
        /// </summary>
        public void ShowTooltip()
        {
            gameObject.SetActive(true);
        }

        /// <summary>
        /// Convenience method for hiding the tooltip.
        /// </summary>
        public void HideTooltip()
        {
            gameObject.SetActive(false);
        }

        #endregion
    }
}