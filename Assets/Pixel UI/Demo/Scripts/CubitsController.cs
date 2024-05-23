using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(RectTransform))]
    [RequireComponent(typeof(Animator))]
    public class CubitsController : MonoBehaviour
    {
        [Tooltip("This is the target that Cubits will run towards while wearing the crop.")]
        public RectTransform MagicTarget;
        [Tooltip("This is the target that Cubits will run towards while not wearing the crop.")]
        public RectTransform ExampleTarget;
        public float Speed = 50f;

        new private RectTransform transform;
        private Animator anim;
        private bool hasCrop = false;

        /// <summary>
        /// Sets whether cubits has the crop attached or not.
        /// </summary>
        public bool HasCrop
        {
            get { return hasCrop; }
            set { hasCrop = value; anim.SetBool("HasCrop", hasCrop); }
        }

        private void Start()
        {
            transform = GetComponent<RectTransform>();
            anim = GetComponent<Animator>();

            ExampleController.Spawned += ExampleController_Spawned;
        }

        private void ExampleController_Spawned(ExampleController sender)
        {
            ExampleTarget = sender.GetComponent<RectTransform>();
        }

        private void Update()
        {
            if (hasCrop && MagicTarget != null)
            {
                ChaseMagicTarget();
            }
            else if (ExampleTarget != null)
            {
                ChaseExampleTarget();
            }
        }

        private void ChaseExampleTarget()
        {
            if (ExampleTarget.anchoredPosition.x < transform.anchoredPosition.x)
            {
                transform.localScale = new Vector3(-1f, 1f, 1f);
            }
            else
            {
                transform.localScale = new Vector3(1f, 1f, 1f);
            }

            transform.anchoredPosition = Vector2.MoveTowards(transform.anchoredPosition, ExampleTarget.anchoredPosition, Speed * Time.deltaTime);
        }

        private void ChaseMagicTarget()
        {
            if (MagicTarget.anchoredPosition.x < transform.anchoredPosition.x)
            {
                transform.localScale = new Vector3(-1f, 1f, 1f);
            }
            else
            {
                transform.localScale = new Vector3(1f, 1f, 1f);
            }

            transform.anchoredPosition = Vector2.MoveTowards(transform.anchoredPosition, MagicTarget.anchoredPosition, Speed * Time.deltaTime);
        }
    }
}