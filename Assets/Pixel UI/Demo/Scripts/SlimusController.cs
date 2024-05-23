using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Image))]
    public class SlimusController : MonoBehaviour
    {
        [TextArea]
        public List<string> DialogueLines = null;
        public UITypewriter typewriter = null;
        public float DialogueWaitTime = 3f;
        public float EventWaitTime = 5f;
        public GameObject ButtonPromptPrefab = null;
        public CubitsController CubitsInstance = null;
        public float ColorChangeSpeed = 0.25f;

        private int currentIndex = -1;
        private bool isBusy = false;
        private GameObject exampleInstance = null;
        private Image image = null;

        public UnityEvent MovePanelEvent;
        public UnityEvent RevealBevelGridEvent;
        public UnityEvent RevealButtonGridEvent;

        private void Awake()
        {
            ExampleController.BeingAttacked += ExampleController_BeingAttacked;
        }

        private void ExampleController_BeingAttacked(ExampleController sender)
        {
            StartCoroutine(ChangeColor(new Color(232f / 255f, 68f / 255f, 68f / 255f), ColorChangeSpeed));
            ExampleController.BeingAttacked -= ExampleController_BeingAttacked;
            ExampleController.AttackStopped += ExampleController_AttackStopped;
        }

        private void ExampleController_AttackStopped(ExampleController sender)
        {
            StartCoroutine(ChangeColor(Color.white, ColorChangeSpeed));
            ExampleController.AttackStopped -= ExampleController_AttackStopped;
        }

        private void Start()
        {
            image = GetComponent<Image>();

            ProgressDialogue(0f);
        }

        public void ProgressDialogue()
        {
            ProgressDialogue(DialogueWaitTime);
        }

        public void ProgressDialogue(float waitTime)
        {
            if (!isBusy)
            {
                isBusy = true;
                StartCoroutine(WaitForNextLine(waitTime));
            }
        }

        private IEnumerator WaitForNextLine(float waitTime)
        {
            var timer = 0f;

            while (timer < waitTime)
            {
                timer += Time.deltaTime;
                yield return null;
            }

            if (currentIndex == 5)
            {
                exampleInstance = Instantiate(ButtonPromptPrefab, GetComponentInParent<Canvas>().transform, false);
                SpeakNextDialogue();
            }
            else if (currentIndex == 8)
            {
                CubitsInstance.HasCrop = true;
                SpeakNextDialogue();
            }
            else if (currentIndex == 11)
            {
                MovePanelEvent.Invoke();
                SpeakNextDialogue();
            }
            else if (currentIndex == 12)
            {
                RevealButtonGridEvent.Invoke();
                SpeakNextDialogue();
            }
            else if (currentIndex == 13)
            {
                RevealBevelGridEvent.Invoke();
                SpeakNextDialogue();
            }
            else
            {
                SpeakNextDialogue();
            }
        }

        private void SpeakNextDialogue()
        {
            currentIndex++;
            if (currentIndex < DialogueLines.Count)
            {
                typewriter.SetText(DialogueLines[currentIndex]);
            }
            else
            {
                Destroy(typewriter.transform.parent.gameObject);
            }

            isBusy = false;
        }

        private IEnumerator ChangeColor(Color color, float duration)
        {
            var timer = 0f;

            while (timer < 1)
            {
                timer += Time.deltaTime / duration;
                image.color = Color.Lerp(Color.white, color, timer);
                yield return null;
            }
        }
    }
}