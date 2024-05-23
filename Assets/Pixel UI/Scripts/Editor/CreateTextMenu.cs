/******************************************************************************************
 * Name: CreateTextMenu.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 02/04/2019
 * Description:
 * Creates a menu for adding text prefabs to the scene.
 ******************************************************************************************/
using UnityEngine;
using UnityEditor;
using System;

namespace PixelsoftGames.PixelUI
{
    [ExecuteInEditMode]
    public class CreateTextMenu : MonoBehaviour
    {
        #region Fields & Properties

        const string skinName = "Text";
        const string skinPath = "Prefabs/Text/";
        const string path = "Prefabs/";

        #endregion

        #if UNITY_EDITOR
            #region Private Static Methods

            [MenuItem("Pixel UI/Create/" + skinName + "/PixelArt Text (Primary)")]
            static void CreatePixelArtTextPrimary()
            {
                InstantiateObj(skinPath + "PixelArt Text (Primary)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/PixelArt Text (Sub)")]
            static void CreatePixelArtTextSub()
            {
                InstantiateObj(skinPath + "PixelArt Text (Sub)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Visitor Text (Primary)")]
            static void CreateVisitorTextPrimary()
            {
                InstantiateObj(skinPath + "Visitor Text (Primary)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Visitor Text (Sub)")]
            static void CreateVisitorTextSub()
            {
                InstantiateObj(skinPath + "Visitor Text (Sub)");
            }

            /// <summary>
            /// Retrieves prefabs from resources and instantiates on a canvas.
            /// </summary>
            static void InstantiateObj(string fullPath)
            {
                var prefab = Resources.Load(fullPath);

                UnityEngine.Object instance = null;
                if (Selection.activeObject != null)
                    instance = Instantiate(prefab, Selection.activeTransform, false);
                else
                {
                    Canvas canvas = GameObject.FindObjectOfType<Canvas>();
                    if (!canvas)
                        canvas = CreateBaseMenu.InstantiateCanvas().gameObject.GetComponent<Canvas>();
                    instance = Instantiate(prefab, canvas.transform, false);
                }

                Selection.objects = new UnityEngine.Object[] { instance };
            }

        #endregion
#endif
    }
}