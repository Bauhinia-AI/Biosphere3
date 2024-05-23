/******************************************************************************************
 * Name: UITypewriter.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * This script will type out the contents of a Text component to add a "typed" effect.
 ******************************************************************************************/
using System.Collections;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Text))]
    public class UITypewriter : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("Should we start typing immediately when this script runs?")]
        private bool playOnStart = false;
        [SerializeField]
        [Tooltip("Should we erase content and start typing again as soon as we finish?")]
        private bool repeat = false;
        [SerializeField]
        [Tooltip("Should we bypass time scale, so that typed messages still work regardless of time scale value?")]
        private bool bypassTimeScale = true;
        [SerializeField]
        [Tooltip("Should we allow skipping if the player presses any button?")]
        private bool allowSkip = true;
        [SerializeField]
        [Tooltip("How slow or fast to type each character")]
        private float TypeDelay = 1500;
        [SerializeField]
        [Tooltip("A special color to make the last typed character for an added visual effect")]
        private Color highlightColor;
        [Tooltip("The event that gets called when the typewriter finishes writing.")]
        public UnityEvent OnComplete;
        [Tooltip("The event that gets called when the typewriter has finished and the user clicks (to progress).")]
        public UnityEvent OnRequestProgress;

        // The text component we will be working with
        private Text label = null;
        // s1 holds the string to be typed, s2 holds what has been typed
        private string s1 = string.Empty, s2 = string.Empty;
        // Index keeps track of where we are in the string
        private int index = 0;
        // The typewriter coroutine reference in case we need to kill it
        private Coroutine typewriter = null;

        #endregion

        #region Monobehaviour Callbacks

        private void Awake()
        {
            label = GetComponent<Text>();
        }

        // Use this for initialization
        private void Start()
        {
            if (playOnStart)
                SetText(label.text);
        }

        // Update is called once per frame
        private void Update()
        {
            if (Input.anyKeyDown)
            {
                if (allowSkip && typewriter != null)
                {
                    if (s1 != null && index != s1.Length)
                    {
                        index = s1.Length;
                        label.text = s1;
                    }

                    FinishCoroutine();
                }
                else if(index == s1.Length && OnRequestProgress != null)
                {
                    OnRequestProgress.Invoke();
                }
            }
        }

        private void OnDestroy()
        {
            StopAllCoroutines();
            OnComplete.RemoveAllListeners();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Tells the typewriter to type out a text string to the connected Text component.
        /// </summary>
        /// <param name="text">The text to type out</param>
        public void SetText(string text)
        {
            if (typewriter != null)
                StopCoroutine(typewriter);

            label.text = string.Empty;
            s1 = text;
            typewriter = StartCoroutine(Typewriter());
        }

        #endregion

        #region Private Methods

        private void FinishCoroutine()
        {
            if (typewriter != null)
            {
                StopCoroutine(typewriter);
                typewriter = null;
            }

            if (OnComplete != null)
                OnComplete.Invoke();
        }

        /// <summary>
        /// This coroutine allows us to bypass time scale.
        /// </summary>
        /// <param name="time">Time to wait</param>
        /// <returns></returns>
        private Coroutine WaitForRealSeconds(float time)
        {
            return StartCoroutine(_WaitForRealSeconds(time));
        }

        #endregion

        #region Coroutines

        /// <summary>
        /// This allows us to bypass timescale pausing so our typewriter still works when our game is paused.
        /// </summary>
        /// <param name="time">Time to wait</param>
        /// <returns></returns>
        private IEnumerator _WaitForRealSeconds(float time)
        {
            while (time > 0f)
            {
                time -= Mathf.Clamp(Time.unscaledDeltaTime, 0, 0.2f);
                yield return null;
            }
        }

        /// <summary>
        /// The actual coroutine that executes the typewriter script.
        /// </summary>
        /// <returns></returns>
        private IEnumerator Typewriter()
        {
            index = 0;
            s2 = string.Empty;
            string colorString = ColorUtility.ToHtmlStringRGBA(highlightColor);

            while (index < s1.Length)
            {
                label.text = s2;
                label.text += "<color=#" + colorString + ">" + s1[index] + "</color>";
                s2 += s1[index];
                index++;

                if (bypassTimeScale)
                    yield return WaitForRealSeconds(60.0f / TypeDelay);
                else
                    yield return new WaitForSeconds(60.0f / TypeDelay);
            }

            label.text = s1;

            if (repeat)
                SetText(label.text);

            FinishCoroutine();
        }

        #endregion
    }
}