/******************************************************************************************
 * Name: UIDialogueWindow.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * This script manages the Dialogue Window.  There are events that can be subscribed to
 * while waiting for a dialogue result.  When the Dialogue Window is instantiated, you
 * need to call the SetData method in this script.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    public class UIDialogueWindow : MonoBehaviour
    {
        #region Events

        public delegate void DialogueEvent(DialogueResultType result);
        /// <summary>
        /// When a button in the dialogue window is clicked the result is calculated and returned
        /// in this event.
        /// </summary>
        public static event DialogueEvent DialogueResult;

        #endregion

        #region Enums

        public enum DialogueType { OK, Cancel, OKCancel, YesNo }
        public enum DialogueResultType { OK, Cancel, Yes, No }

        #endregion

        #region Fields & Properties

        [SerializeField]
        [Tooltip("Reference to the negative response button")]
        private Button declineButton = null;
        [SerializeField]
        [Tooltip("Reference to the positive response button")]
        private Button confirmButton = null;
        [SerializeField]
        [Tooltip("The title to display at the top of the window")]
        private Text title = null;
        [SerializeField]
        [Tooltip("The message to display in the window body.")]
        private Text message = null;

        private DialogueType type = DialogueType.Cancel;

        #endregion

        #region Public Methods

        /// <summary>
        /// A required method for the essential functioning of the dialogue window.  This will set the title text,
        /// window message, and button texts.
        /// </summary>
        /// <param name="type">The type of dialogue window to create</param>
        /// <param name="title">The text to be displayed in the title area</param>
        /// <param name="message">The text to be displayed in the message area</param>
        public void SetData(DialogueType type, string title, string message)
        {
            if (string.IsNullOrEmpty(title) || string.IsNullOrEmpty(message))
            {
                Debug.LogError("Could not create a dialogue window because some of the requested data is null or empty.", gameObject);
                Destroy(gameObject);
                return;
            }

            this.type = type;
            this.title.text = title;
            this.message.text = message;

            switch (type)
            {
                case DialogueType.Cancel:
                    declineButton.GetComponentInChildren<Text>().text = "Cancel";
                    confirmButton.gameObject.SetActive(false);
                    break;
                case DialogueType.OK:
                    declineButton.gameObject.SetActive(false);
                    confirmButton.GetComponentInChildren<Text>().text = "OK";
                    break;
                case DialogueType.OKCancel:
                    declineButton.GetComponentInChildren<Text>().text = "Cancel";
                    confirmButton.GetComponentInChildren<Text>().text = "OK";
                    break;
                case DialogueType.YesNo:
                    declineButton.GetComponentInChildren<Text>().text = "No";
                    confirmButton.GetComponentInChildren<Text>().text = "Yes";
                    break;
            }
        }

        /// <summary>
        /// Called by the confirm button when clicked
        /// </summary>
        public void OnConfirmButton_Clicked()
        {
            PrintResult(true);
            Destroy(gameObject);
        }

        /// <summary>
        /// Called by the decline button when clicked
        /// </summary>
        public void OnDeclineButton_Clicked()
        {
            PrintResult(false);
            Destroy(gameObject);
        }

        #endregion

        #region Private Methods

        /// <summary>
        /// Parses and raises the result event if there are any listeners
        /// </summary>
        /// <param name="isConfirmed">Whether the confirm button was clicked or not</param>
        private void PrintResult(bool isConfirmed)
        {
            if (DialogueResult != null)
            {
                switch (type)
                {
                    case DialogueType.Cancel:
                        DialogueResult(DialogueResultType.Cancel);
                        break;
                    case DialogueType.OK:
                        DialogueResult(DialogueResultType.OK);
                        break;
                    case DialogueType.OKCancel:
                        if (isConfirmed)
                            DialogueResult(DialogueResultType.OK);
                        else
                            DialogueResult(DialogueResultType.Cancel);
                        break;
                    case DialogueType.YesNo:
                        if (isConfirmed)
                            DialogueResult(DialogueResultType.Yes);
                        else
                            DialogueResult(DialogueResultType.No);
                        break;
                }
            }
        }

        #endregion
    }
}