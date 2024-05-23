/******************************************************************************************
 * Name: UITabbedWindow.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * This script controls the hiding and showing of content panes for each tab.  If you need
 * to add more tabs, in the hiearchy duplicate one of the existing tabs and change its
 * ID to be one higher than the current highest.  Then duplicate a content pane as well
 * and extend the ContentPanes count in the inspector and attach the new content pane
 * to the last slot.
 ******************************************************************************************/
using System.Collections.Generic;
using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    public class UITabbedWindow : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("List of content panes for this tabbed window")]
        private List<GameObject> ContentPanes = null;
        [SerializeField]
        [Tooltip("The default pane to display on instantiation")]
        private GameObject DefaultPane = null;

        // The currently active pane
        private GameObject activePane = null;

        #endregion

        #region Monobehaviour Callbacks

        private void Start()
        {
            SetupContent();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// This changes the active content pane and deactivates the previously active one.
        /// </summary>
        /// <param name="index"></param>
        public void ActivateContentPane(int index)
        {
            if (ContentPanes == null || index >= ContentPanes.Count)
            {
                Debug.LogError("Could not switch to the requested content pane because the requested pane index is out of bounds or the content panes list is null.", gameObject);
                return;
            }

            activePane.SetActive(false);
            activePane = ContentPanes[index];
            activePane.SetActive(true);
        }

        #endregion

        #region Private Methods

        /// <summary>
        /// This method is called on startup and validates the tabbed window, deactivates inactive windows and activates the default. 
        /// </summary>
        private void SetupContent()
        {
            if (ContentPanes == null || ContentPanes.Count == 0)
            {
                Debug.LogError("Could not set up content panes because the content panes list is null or empty.", gameObject);
                return;
            }

            if (DefaultPane == null)
            {
                Debug.LogWarning("No default pane for tabbed window has been set up, choosing the first pane in the list by default", gameObject);
                DefaultPane = ContentPanes[0];
            }

            activePane = DefaultPane;

            foreach (GameObject g in ContentPanes)
            {
                if (g == activePane)
                    g.SetActive(true);
                else
                    g.SetActive(false);
            }
        }

        #endregion
    }
}
