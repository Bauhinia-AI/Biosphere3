/******************************************************************************************
 * Name: CreateExtrasMenu.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 02/27/2019
 * Description:
 * Creates a menu for adding custom Pixel UI control prefabs to the scene.
 ******************************************************************************************/
using UnityEngine;
using UnityEditor;
using System;

namespace PixelsoftGames.PixelUI
{
    public class CreateExtrasMenu : MonoBehaviour
    {
        #region Fields & Properties

        const string skinName = "Extras";
        const string skinPath = "Prefabs/Extras/";
        const string path = "Prefabs/";

        #endregion

#if UNITY_EDITOR
        #region Private Static Methods
            [MenuItem("Pixel UI/Create/" + skinName + "/Tooltip")]
            static void CreateTooltip()
            {
                InstantiateObj(skinPath + "Tooltip");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Health Bar (Horizontal)")]
            static void CreateHorizontalHealthBar()
            {
                InstantiateObj(skinPath + "Health Bar (Horizontal)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Health Bar (Vertical)")]
            static void CreateVerticalHealthBar()
            {
                InstantiateObj(skinPath + "Health Bar (Vertical)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Mana Bar (Horizontal)")]
            static void CreateHorizontalManaBar()
            {
                InstantiateObj(skinPath + "Mana Bar (Horizontal)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Mana Bar (Vertical)")]
            static void CreateVerticalManaBar()
            {
                InstantiateObj(skinPath + "Mana Bar (Vertical)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Energy Bar (Horizontal)")]
            static void CreateHorizontalEnergyBar()
            {
                InstantiateObj(skinPath + "Energy Bar (Horizontal)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Energy Bar (Vertical)")]
            static void CreateVerticalEnergyBar()
            {
                InstantiateObj(skinPath + "Energy Bar (Vertical)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Experience Bar (Horizontal)")]
            static void CreateHorizontalExperienceBar()
            {
                InstantiateObj(skinPath + "Experience Bar (Horizontal)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Experience Bar (Vertical)")]
            static void CreateVerticalExperienceBar()
            {
                InstantiateObj(skinPath + "Experience Bar (Vertical)");
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