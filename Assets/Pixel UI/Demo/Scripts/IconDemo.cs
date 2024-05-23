using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    public class IconDemo : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        string iconResourcePath = string.Empty;
        [SerializeField]
        Texture2D iconSheet = null;
        [SerializeField]
        GameObject demoIconPrefab = null;
        [SerializeField]
        Transform contentPane = null;

        #endregion

        #region Monobehavior Callbacks

        private void Start()
        {
            LoadIconDemo();
        }

        #endregion

        #region Private Methods

        void LoadIconDemo()
        {
            Sprite[] icons = Resources.LoadAll<Sprite>(iconResourcePath + iconSheet.name);
            foreach(Sprite icon in icons)
            {
                GameObject demoIcon = Instantiate(demoIconPrefab, contentPane, false);
                foreach (Image image in demoIcon.transform.GetComponentsInChildren<Image>())
                    if (image.gameObject != demoIcon)
                        image.sprite = icon;
            }
        }

        #endregion
    }
}