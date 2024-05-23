/******************************************************************************************
 * Name: LoadScene.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * A demo script that can be easily attached to a button to implement scene changing
 * on click.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.SceneManagement;

namespace PixelsoftGames.PixelUI
{
    public class LoadScene : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("The index of the scene to load on click.")]
        int indexToLoad = -1;

        #endregion

        #region Callbacks

        /// <summary>
        /// Executed when the button is clicked.
        /// </summary>
        public void On_Click()
        {
            if (indexToLoad == -1)
                return;

            SceneManager.LoadScene(indexToLoad);
        }

        #endregion
    }
}