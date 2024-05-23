/******************************************************************************************
 * Name: UICard.cs
 * Created by: Jeremy Voss
 * Created on: 03/01/2019
 * Last Modified: 04/29/2019
 * Description:
 * A script designed to be used with the new pixel cards.  This script contains a number
 * of useful features to accompany these cards.  Features include the ability to peek
 * or flip cards, fade card features, etc.
 ******************************************************************************************/
using System.Collections;
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    public class UICard : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("The blank (black background) displayed behind a card.")]
        private GameObject cardBlank = null;
        public Image Blank { get { return cardBlank.GetComponent<Image>(); } }

        [SerializeField]
        [Tooltip("The background displayed on a card (front or back).")]
        private GameObject cardBackground = null;
        public Image Background { get { return cardBackground.GetComponent<Image>(); } }

        [SerializeField]
        [Tooltip("The foreground displayed on a card, typically modifiers.")]
        private GameObject cardForeground = null;
        public Image Foreground { get { return cardForeground.GetComponent<Image>(); } }

        [SerializeField]
        [Tooltip("The object containing the name of this card.")]
        private GameObject cardName = null;
        public Text Name { get { return cardName.GetComponent<Text>(); } }

        [SerializeField]
        [Tooltip("The object containing the modifier information of this card.")]
        private GameObject cardModifier = null;
        public Text Modifier { get { return cardModifier.GetComponent<Text>(); } }

        [SerializeField]
        [Tooltip("The object containing the description of this card.")]
        private GameObject cardDescription = null;
        public Text Description { get { return cardDescription.GetComponent<Text>(); } }

        [SerializeField]
        [Tooltip("The object displaying the icon associated with this card.")]
        private GameObject cardIcon = null;
        public Image Icon { get { return cardIcon.GetComponent<Image>(); } }

        /// <summary>
        /// The sprite used when the card is flipped back side up.
        /// </summary>
        public Sprite cardBackSprite = null;
        /// <summary>
        /// The sprite used when the card is flipped front side up.
        /// </summary>
        public Sprite cardFrontSprite = null;

        // Used to store any actively running coroutine.
        private Coroutine currentCoroutine = null;
        // Whether the card is revealed or not
        private bool isRevealed = false;

        #endregion

        #region Monobehavior Callbacks

        private void OnDestroy()
        {
            if (currentCoroutine != null)
            {
                StopCoroutine(currentCoroutine);
            }
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// This will reset all the data on the card (good for recycling cards).
        /// </summary>
        public void Reset()
        {
            isRevealed = false;
            Background.sprite = cardBackSprite;

            Blank.sprite = null;
            HideBlank();
            Foreground.sprite = null;
            HideForeground();
            Icon.sprite = null;
            HideIcon();
            Name.text = string.Empty;
            HideName();
            Modifier.text = string.Empty;
            HideModifier();
            Description.text = string.Empty;
            HideDescription();
        }

        /// <summary>
        /// Allows a quick peek (reveal) at the card before turning it back over.
        /// </summary>
        /// <param name="duration">The amount of time the card should be revealed for.</param>
        public void Peek(float flipDuration, float fadeDuration, float peekDuration)
        {
            currentCoroutine = StartCoroutine(PerformPeek(flipDuration, fadeDuration, peekDuration));
        }

        /// <summary>
        /// Moves the card one position to another.  (i.e. - from the deck to its position). 
        /// </summary>
        /// <param name="position">The target position for the card to move to.</param>
        /// <param name="reveal">Should we reveal the card after moving?</param>
        /// <param name="showBlank">Should we show the blank after moving the card?</param>
        public void MoveToPosition(Vector3 position, bool reveal, bool showBlank, float moveDuration, float flipDuration = 0f)
        {
            currentCoroutine = StartCoroutine(MovePosition(position, reveal, showBlank, moveDuration, flipDuration));
        }

        /// <summary>
        /// Instantly hides the card blank.
        /// </summary>
        public void HideBlank()
        {
            Color c = Blank.color;
            Blank.color = new Color(c.r, c.g, c.b, 0f);
        }

        /// <summary>
        /// Instantly shows the card blank.
        /// </summary>
        public void ShowBlank()
        {
            Color c = Blank.color;
            Blank.color = new Color(c.r, c.g, c.b, 1f);
        }

        /// <summary>
        /// Fades out the card blank.
        /// </summary>
        public void FadeOutBlank()
        {
            cardBlank.GetComponent<UIFader>().FadeOut();
        }

        /// <summary>
        /// Fades in the card blank.
        /// </summary>
        public void FadeInBlank()
        {
            cardBlank.GetComponent<UIFader>().FadeIn();
        }

        /// <summary>
        /// Instantly hides the card foreground.
        /// </summary>
        public void HideForeground()
        {
            Color c = Foreground.color;
            Foreground.color = new Color(c.r, c.g, c.b, 0f);
        }

        /// <summary>
        /// Instantly shows the card foreground.
        /// </summary>
        public void ShowForeground()
        {
            Color c = Foreground.color;
            Foreground.color = new Color(c.r, c.g, c.b, 1f);
        }

        /// <summary>
        /// Fades out the card foreground.
        /// </summary>
        public void FadeOutForeground()
        {
            cardForeground.GetComponent<UIFader>().FadeOut();
        }

        /// <summary>
        /// Fades in the card foreground.
        /// </summary>
        public void FadeInForeground()
        {
            cardForeground.GetComponent<UIFader>().FadeIn();
        }

        /// <summary>
        /// Instantly hides the card name.
        /// </summary>
        public void HideName()
        {
            Color c = Name.color;
            Name.color = new Color(c.r, c.g, c.b, 0f);
        }

        /// <summary>
        /// Instantly shows the card name.
        /// </summary>
        public void ShowName()
        {
            Color c = Name.color;
            Name.color = new Color(c.r, c.g, c.b, 1f);
        }

        /// <summary>
        /// Fades out the card name.
        /// </summary>
        public void FadeOutName()
        {
            cardName.GetComponent<UIFader>().FadeOut();
        }

        /// <summary>
        /// Fades in the card name.
        /// </summary>
        public void FadeInName()
        {
            cardName.GetComponent<UIFader>().FadeIn();
        }

        /// <summary>
        /// Instantly hides the card modifier.
        /// </summary>
        public void HideModifier()
        {
            Color c = Modifier.color;
            Modifier.color = new Color(c.r, c.g, c.b, 0f);
        }

        /// <summary>
        /// Instantly shows the card modifier.
        /// </summary>
        public void ShowModifier()
        {
            Color c = Modifier.color;
            Modifier.color = new Color(c.r, c.g, c.b, 1f);
        }

        /// <summary>
        /// Fades out the card modifier.
        /// </summary>
        public void FadeOutModifier()
        {
            cardModifier.GetComponent<UIFader>().FadeOut();
        }

        /// <summary>
        /// Fades in the card modifier.
        /// </summary>
        public void FadeInModifier()
        {
            cardModifier.GetComponent<UIFader>().FadeIn();
        }

        /// <summary>
        /// Instantly hides the card description.
        /// </summary>
        public void HideDescription()
        {
            Color c = Description.color;
            Description.color = new Color(c.r, c.g, c.b, 0f);
        }

        /// <summary>
        /// Instantly shows the card description.
        /// </summary>
        public void ShowDescription()
        {
            Color c = Description.color;
            Description.color = new Color(c.r, c.g, c.b, 1f);
        }

        /// <summary>
        /// Fades out the card description.
        /// </summary>
        public void FadeOutDescription()
        {
            cardDescription.GetComponent<UIFader>().FadeOut();
        }

        /// <summary>
        /// Fades in the card description.
        /// </summary>
        public void FadeInDescription()
        {
            cardDescription.GetComponent<UIFader>().FadeIn();
        }

        /// <summary>
        /// Instantly hides the card icon.
        /// </summary>
        public void HideIcon()
        {
            Color c = Icon.color;
            Icon.color = new Color(c.r, c.g, c.b, 0f);
        }

        /// <summary>
        /// Instantly shows the card icon.
        /// </summary>
        public void ShowIcon()
        {
            Color c = Icon.color;
            Icon.color = new Color(c.r, c.g, c.b, 1f);
        }

        /// <summary>
        /// Fades out the card icon.
        /// </summary>
        public void FadeOutIcon()
        {
            cardIcon.GetComponent<UIFader>().FadeOut();
        }

        /// <summary>
        /// Fades in the card icon.
        /// </summary>
        public void FadeInIcon()
        {
            cardIcon.GetComponent<UIFader>().FadeIn();
        }

        /// <summary>
        /// Flips the card over to display the front.
        /// </summary>
        public void FlipToFront(float flipDuration)
        {
            currentCoroutine = StartCoroutine(FlipFront(flipDuration));
        }

        /// <summary>
        /// Flips the card over to display the back.
        /// </summary>
        public void FlipToBack(float flipDuration, float fadeDuration)
        {
            currentCoroutine = StartCoroutine(FlipBack(flipDuration, fadeDuration));
        }

        /// <summary>
        /// Flips the card to its opposite side.
        /// </summary>
        public void Flip(float flipDuration, float fadeDuration)
        {
            if (isRevealed)
            {
                FlipToBack(flipDuration, fadeDuration);
            }
            else
            {
                FlipToFront(flipDuration);
            }
        }

        #endregion

        #region Coroutines

        /// <summary>
        /// 
        /// </summary>
        /// <param name="flipDuration">Amount of time to wait for flipping.</param>
        /// <param name="fadeDuration">Amount of time to wait for fading.</param>
        /// <param name="peekDuration">Amount of time to wait for peeking.</param>
        /// <returns></returns>
        private IEnumerator PerformPeek(float flipDuration, float fadeDuration, float peekDuration)
        {
            StartCoroutine(FlipFront(flipDuration));
            yield return new WaitForSeconds(flipDuration + fadeDuration + peekDuration);
            StartCoroutine(FlipBack(flipDuration, fadeDuration));

            yield return null;
        }

        /// <summary>
        /// Moves a card from one position to another.
        /// </summary>
        /// <param name="position">The position to move to.</param>
        /// <param name="reveal">Should we reveal the card after moving?</param>
        /// <param name="showBlank">Should we display the blank after moving?</param>
        /// <returns></returns>
        private IEnumerator MovePosition(Vector3 position, bool reveal, bool showBlank, float moveTime, float flipDuration = 0f)
        {
            float timer = 0f;
            RectTransform t = GetComponent<RectTransform>();
            Vector3 startPosition = t.anchoredPosition;

            while (timer < moveTime)
            {
                timer += Time.deltaTime;
                t.anchoredPosition = Vector3.Lerp(startPosition, position, timer / moveTime);
                yield return null;
            }

            if (showBlank)
            {
                FadeInBlank();
            }

            if (reveal)
            {
                currentCoroutine = StartCoroutine(FlipFront(flipDuration));
            }
        }

        /// <summary>
        /// Flips the card over and displays the front of the card.
        /// </summary>
        /// <returns></returns>
        private IEnumerator FlipFront(float flipDuration)
        {
            float targetAngle = 90f;
            float timer = 0f;

            // Flip halfway
            while (timer < flipDuration * 0.5f)
            {
                timer += Time.deltaTime;
                cardBackground.transform.rotation = Quaternion.Slerp(cardBackground.transform.rotation, 
                    Quaternion.Euler(Vector3.up * targetAngle), timer / flipDuration);
                yield return null;
            }

            // Change card sprite
            Background.sprite = cardFrontSprite;
            targetAngle = 360f;
            timer = 0f;
            // Show card components
            ShowForeground();
            ShowName();
            ShowModifier();
            ShowDescription();
            ShowIcon();

            // Continue the flip
            while (timer < flipDuration * 0.5f)
            {
                timer += Time.deltaTime;
                cardBackground.transform.rotation = Quaternion.Slerp(cardBackground.transform.rotation,
                    Quaternion.Euler(Vector3.up * targetAngle), timer / flipDuration);
                yield return null;
            }

            // Reset rotation to 0
            cardBackground.transform.rotation = Quaternion.identity;

            isRevealed = true;
        }

        /// <summary>
        /// Flips the card over and displays the back of the card.
        /// </summary>
        /// <returns></returns>
        private IEnumerator FlipBack(float flipDuration, float fadeDuration)
        {
            float targetAngle = 90f;
            float timer = 0f;

            // yield return new WaitForSeconds(fadeDuration);

            // Flip halfway
            while(timer < flipDuration * 0.5f)
            {
                timer += Time.deltaTime;
                cardBackground.transform.rotation = Quaternion.Slerp(cardBackground.transform.rotation,
                    Quaternion.Euler(Vector3.up * targetAngle), timer / flipDuration);
                yield return null;
            }

            // Change card sprite
            Background.sprite = cardBackSprite;
            targetAngle = 360f;
            timer = 0f;
            // Hide card components
            HideForeground();
            HideName();
            HideModifier();
            HideDescription();
            HideIcon();

            // Continue the flip
            while (timer < flipDuration * 0.5f)
            {
                timer += Time.deltaTime;
                cardBackground.transform.rotation = Quaternion.Slerp(cardBackground.transform.rotation,
                    Quaternion.Euler(Vector3.up * targetAngle), timer / flipDuration);
                yield return null;
            }

            // Reset rotation to 0
            cardBackground.transform.rotation = Quaternion.identity;

            isRevealed = false;
        }

        #endregion
    }
}