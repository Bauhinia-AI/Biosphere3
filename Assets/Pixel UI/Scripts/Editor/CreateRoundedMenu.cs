/******************************************************************************************
 * Name: CreateRoundedMenu.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 02/04/2019
 * Description:
 * Creates a menu for adding Rounded themed prefabs to the scene.
 ******************************************************************************************/
using UnityEngine;
using UnityEditor;
using System;

namespace PixelsoftGames.PixelUI
{
    public class CreateRoundedMenu : MonoBehaviour
    {
        #region Fields & Properties

        const string skinName = "Rounded";
        const string skinPath = "Prefabs/Rounded/";
        const string path = "Prefabs/";

        #endregion

        #if UNITY_EDITOR
            #region Private Static Methods

            [MenuItem("Pixel UI/Create/" + skinName + "/Thought Bubble (Left)")]
            static void CreateLeftThoughtBubble()
            {
                InstantiateObj(skinPath + "Thought Bubble (Left)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Thought Bubble (Right)")]
            static void CreateRightThoughtBubble()
            {
                InstantiateObj(skinPath + "Thought Bubble (Right)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Shadow Thought Bubble (Left)")]
            static void CreateLeftShadowThoughtBubble()
            {
                InstantiateObj(skinPath + "Shadow Thought Bubble (Left)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Shadow Thought Bubble (Right)")]
            static void CreateRightShadowThoughtBubble()
            {
                InstantiateObj(skinPath + "Shadow Thought Bubble (Right)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Dialogue Bubble (Left)")]
            static void CreateLeftDialogueBubble()
            {
                InstantiateObj(skinPath + "Dialogue Bubble (Left)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Dialogue Bubble (Right)")]
            static void CreateRightDialogueBubble()
            {
                InstantiateObj(skinPath + "Dialogue Bubble (Right)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Shadow Dialogue Bubble (Left)")]
            static void CreateLeftShadowDialogueBubble()
            {
                InstantiateObj(skinPath + "Shadow Dialogue Bubble (Left)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Shadow Dialogue Bubble (Right)")]
            static void CreateRightShadowDialogueBubble()
            {
                InstantiateObj(skinPath + "Shadow Dialogue Bubble (Right)");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Dialogue Window")]
            static void CreateDialogueWindow()
            {
                InstantiateObj(skinPath + "Dialogue Window");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Tabbed Window")]
            static void CreateTabbedWindow()
            {
                InstantiateObj(skinPath + "Tabbed Window");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Window")]
            static void CreateWindow()
            {
                InstantiateObj(skinPath + "Window");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Scroll View")]
            static void CreateScrollView()
            {
                InstantiateObj(skinPath + "Scroll View");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Button")]
            static void CreateButton()
            {
                InstantiateObj(skinPath + "Button");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Shadow Button")]
            static void CreateShadowButton()
            {
                InstantiateObj(skinPath + "Shadow Button");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Dropdown")]
            static void CreateDropdown()
            {
                InstantiateObj(skinPath + "Dropdown");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Shadow Dropdown")]
            static void CreateShadowDropdown()
            {
                InstantiateObj(skinPath + "Shadow Dropdown");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Input")]
            static void CreateInput()
            {
                InstantiateObj(skinPath + "Input");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Shadow Input")]
            static void CreateShadowInput()
            {
                InstantiateObj(skinPath + "Shadow Input");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Panel")]
            static void CreatePanel()
            {
                InstantiateObj(skinPath + "Panel");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Radio Button")]
            static void CreateRadioButton()
            {
                InstantiateObj(skinPath + "Radio Button");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Scrollbar")]
            static void CreateScrollbar()
            {
                InstantiateObj(skinPath + "Scrollbar");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Shadow Scrollbar")]
            static void CreateShadowScrollbar()
            {
                InstantiateObj(skinPath + "Shadow Scrollbar");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Slider")]
            static void CreateSlider()
            {
                InstantiateObj(skinPath + "Slider");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Checkmark Toggle")]
            static void CreateToggleCheckmark()
            {
                InstantiateObj(skinPath + "Checkmark Toggle");
            }

            [MenuItem("Pixel UI/Create/" + skinName + "/Cross Toggle")]
            static void CreateCrossToggle()
            {
                InstantiateObj(skinPath + "Cross Toggle");
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