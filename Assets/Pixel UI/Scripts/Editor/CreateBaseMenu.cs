/******************************************************************************************
 * Name: CreateBaseMenu.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 02/04/2019
 * Description:
 * Creates a menu for adding base Pixel UI essential prefabs to the scene.
 ******************************************************************************************/
using UnityEngine;
using UnityEditor;
using System;
using UnityEngine.EventSystems;

namespace PixelsoftGames.PixelUI
{
    public class CreateBaseMenu : MonoBehaviour
    {
        #region Fields & Properties

        const string skinName = "";
        const string skinPath = "Prefabs/";
        const string path = "Prefabs/";

        #endregion

#if UNITY_EDITOR
        #region Private Static Methods

        [MenuItem("Pixel UI/Create/Pixel UI Canvas")]
        static void CreatePixelUICanvas()
        {
            InstantiateCanvas();
        }

        /// <summary>
        /// Retrieves prefabs from resources and instantiates on a canvas.
        /// </summary>
        public static Transform InstantiateCanvas()
        {
            var prefab = Resources.Load(path + "Pixel UI Canvas");
            GameObject canvas = Instantiate(prefab, null, false) as GameObject;
            canvas.name = "Canvas";
            var eventSystemPrefab = Resources.Load(path + "EventSystem");
            GameObject eventSystem = Instantiate(eventSystemPrefab, null, true) as GameObject;
            eventSystem.name = "EventSystem";

            return canvas.transform;
        }
    }

    #endregion
#endif
}