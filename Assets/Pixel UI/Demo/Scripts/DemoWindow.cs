/******************************************************************************************
 * Name: DemoWindow.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * A demo script that spawns a demo window so the user can see the new window feature.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    public class DemoWindow : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("The window prefab to spawn.")]
        GameObject WindowPrefab;

        GameObject windowInstance = null;
        Text label;

        #endregion

        #region Monobehaviour Callbacks

        private void Start()
        {
            label = GetComponentInChildren<Text>();
        }

        #endregion

        #region Callbacks

        /// <summary>
        /// When the button is clicked we will spawn an instance of the prefab and change the state of the button.
        /// </summary>
        public void On_Click()
        {
            if(windowInstance != null)
            {
                Destroy(windowInstance);
                label.text = "Spawn Window";
            }
            else
            {
                Transform canvas = GameObject.Find("Canvas").transform;
                windowInstance = Instantiate(WindowPrefab, canvas, false);
                label.text = "Close Window";
            }
        }

        #endregion
    }
}