/******************************************************************************************
 * Name: DemoDialogue.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * A simple demo script that spawns a random dialogue box so the user can demo the
 * various dialogue box types.
 ******************************************************************************************/
using System;
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Button))]
    public class DemoDialogue : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("The dialogue window prefab to spawn")]
        GameObject DialoguePrefab;

        GameObject dialogueInstance = null;
        Button button;

        #endregion

        #region Monobehaviour Callbacks

        private void Awake()
        {
            button = GetComponent<Button>();
        }

        private void OnDestroy()
        {
            UIDialogueWindow.DialogueResult -= On_DialogueResult;
        }

        #endregion

        #region Callbacks

        /// <summary>
        /// When we receive the dialogue result we know the window has been closed so we can re-enable the button.
        /// </summary>
        /// <param name="result">The returned dialogue result (unused)</param>
        private void On_DialogueResult(UIDialogueWindow.DialogueResultType result)
        {
            UIDialogueWindow.DialogueResult -= On_DialogueResult;
            button.interactable = true;
        }

        /// <summary>
        /// Instantiates a random type of dialogue window whenever the button is clicked and disables the button
        /// until that window is closed.
        /// </summary>
        public void On_Click()
        {
            Transform canvas = GameObject.Find("Canvas").transform;
            dialogueInstance = Instantiate(DialoguePrefab, canvas, false);
            button.interactable = false;
            UIDialogueWindow.DialogueResult += On_DialogueResult;
            dialogueInstance.GetComponent<UIDialogueWindow>().SetData((UIDialogueWindow.DialogueType)UnityEngine.Random.Range(0, Enum.GetValues(typeof(UIDialogueWindow.DialogueType)).Length), 
                "Demo Dialogue Window", "This is a sample dialogue window");
        }

        #endregion
    }
}