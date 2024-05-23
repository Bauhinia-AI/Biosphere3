/******************************************************************************************
 * Name: UIFader.cs
 * Created by: Jeremy Voss
 * Created on: 02/20/2019
 * Last Modified: 02/20/2019
 * Description:
 * The UI Fader is responsible for fading in/out UI elements.  It can target either an Image
 * or a Text element and even be set to toggle between fading in/out automatically.  Please
 * be sure to attach the proper element to the same GameObject as this script and toggle
 * the IsText checkbox appropriately.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    public class UIFader : MonoBehaviour
    {
        #region Fields & Properties

        public enum FadeMode { None, In, Out, PingPong }
        public enum ComponentType { Text, Image, CanvasGroup }

        [SerializeField]
        [Tooltip("The start mode of the fader.")]
        private FadeMode mode = FadeMode.None;
        [SerializeField]
        [Tooltip("What type of component will we be fading?")]
        private ComponentType componentType = ComponentType.Image;
        [SerializeField]
        [Tooltip("The amount of time given for each fade transition.")]
        private float fadeTime = 1f;
        [SerializeField]
        [Tooltip("Should we destroy the GameObject after fade out is complete?")]
        private bool destroyOnFadeOut = false;

        public UnityEvent OnFadeOutComplete = null, OnFadeInComplete = null;

        /// <summary>
        /// If we are fading an image, this will be our target image.
        /// </summary>
        private Image image = null;
        /// <summary>
        /// If we are fading a text, this will be our target text.
        /// </summary>
        private Text text = null;
        /// <summary>
        /// If we are fading a canvas group, this will be our target group.
        /// </summary>
        private CanvasGroup canvasGroup = null;
        /// <summary>
        /// The current state of the fader.
        /// </summary>
        private FadeMode currentState = FadeMode.None;
        /// <summary>
        /// The default and fade out colors for the fader to target.
        /// </summary>
        private Color defaultColor, fadeOutColor;
        /// <summary>
        /// The timer that keeps track of our fade time.
        /// </summary>
        private float timer = 0f;
        /// <summary>
        /// Tells us if this component has been initialized before we try to use it.
        /// </summary>
        private bool isInitialized = false;

        #endregion

        #region Monobehavior Callbacks

        private void Start()
        {
            Initialize();
        }

        private void Update()
        {
            switch(currentState)
            {
                case FadeMode.In: // Fading In
                    FadeIn();
                    break;
                case FadeMode.Out: // Fading Out
                    FadeOut();
                    break;
                case FadeMode.PingPong: // Fading In/Out
                    if (currentState == FadeMode.In)
                    {
                        FadeIn();
                    }
                    else
                    {
                        FadeOut();
                    }
                    break;
            }
        }

        private void OnDestroy()
        {
            OnFadeOutComplete.RemoveAllListeners();
            OnFadeInComplete.RemoveAllListeners();
        }

        #endregion

        #region Private Methods

        private void Initialize()
        {
            if (isInitialized)
            {
                return;
            }

            isInitialized = true;

            currentState = mode;

            switch (componentType)
            {
                case ComponentType.CanvasGroup: // Canvas Group
                    canvasGroup = GetComponent<CanvasGroup>();
                    break;
                case ComponentType.Image: // Image
                    image = GetComponent<Image>();
                    defaultColor = new Color(image.color.r, image.color.g, image.color.b);
                    break;
                case ComponentType.Text: // Text
                    text = GetComponent<Text>();
                    defaultColor = new Color(text.color.r, text.color.g, text.color.b);
                    break;
            }

            if (componentType != ComponentType.CanvasGroup)
            {
                fadeOutColor = new Color(defaultColor.r, defaultColor.g, defaultColor.b, 0f);
            }

            if (mode == FadeMode.PingPong)
            {
                currentState = FadeMode.Out;
            }
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Triggers fading in the target UI element.
        /// </summary>
        public void FadeIn()
        {
            if (!isInitialized)
            {
                Initialize();
            }

            if (currentState != FadeMode.In)
            {
                timer = 0f;
                currentState = FadeMode.In;
            }

            timer += Time.deltaTime;
            bool fadeComplete = false;

            switch(componentType)
            {
                case ComponentType.CanvasGroup: // Canvas Group
                    if (canvasGroup.alpha != 1f)
                    {
                        canvasGroup.alpha = Mathf.Lerp(0f, 1f, timer / fadeTime);
                    }
                    else
                    {
                        fadeComplete = true;
                    }
                    break;
                case ComponentType.Image: // Image
                    if (image.color != defaultColor)
                    {
                        image.color = Color.Lerp(fadeOutColor, defaultColor, timer / fadeTime);
                    }
                    else
                    {
                        fadeComplete = true;
                    }
                    break;
                case ComponentType.Text: // Text
                    if (text.color != defaultColor)
                    {
                        text.color = Color.Lerp(fadeOutColor, defaultColor, timer / fadeTime);
                    }
                    else
                    {
                        fadeComplete = true;
                    }
                    break;
            }

            if (fadeComplete)
            {
                CompleteFadeIn();
            }
        }

        /// <summary>
        /// Triggers fading out the target UI element.
        /// </summary>
        public void FadeOut()
        {
            if (!isInitialized)
            {
                Initialize();
            }

            if (currentState != FadeMode.Out)
            {
                currentState = FadeMode.Out;
                timer = 0f;
            }

            timer += Time.deltaTime;
            bool fadeComplete = false;

            switch (componentType)
            {
                case ComponentType.CanvasGroup: // Canvas Group
                    if (canvasGroup.alpha != 0f)
                    {
                        canvasGroup.alpha = Mathf.Lerp(1f, 0f, timer / fadeTime);
                    }
                    else
                    {
                        fadeComplete = true;
                    }
                    break;
                case ComponentType.Image: // Image
                    if (image.color != fadeOutColor)
                    {
                        image.color = Color.Lerp(defaultColor, fadeOutColor, timer / fadeTime);
                    }
                    else
                    {
                        fadeComplete = true;
                    }
                    break;
                case ComponentType.Text: // Text
                    if (text.color != fadeOutColor)
                    {
                        text.color = Color.Lerp(defaultColor, fadeOutColor, timer / fadeTime);
                    }
                    else
                    {
                        fadeComplete = true;
                    }
                    break;
            }

            if (fadeComplete)
            {
                CompleteFadeOut();
            }
        }

        private void CompleteFadeOut()
        {
            if (OnFadeOutComplete != null)
            {
                OnFadeOutComplete.Invoke();
            }

            if (destroyOnFadeOut)
            {
                Destroy(gameObject);
            }
            else if (mode == FadeMode.PingPong)
            {
                FadeIn();
            }
            else
            {
                mode = FadeMode.None;
                currentState = FadeMode.None;
            }
        }

        private void CompleteFadeIn()
        {
            if (OnFadeInComplete != null)
            {
                OnFadeInComplete.Invoke();
            }

            if (mode == FadeMode.PingPong)
            {
                FadeOut();
            }
            else
            {
                mode = FadeMode.None;
                currentState = FadeMode.None;
            }
        }

        #endregion
    }
}