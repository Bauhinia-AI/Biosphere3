using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Shake))]
    [RequireComponent(typeof(Image))]
    [RequireComponent(typeof(BoxCollider2D))]
    public class ExampleController : MonoBehaviour
    {
        public delegate void ExampleControllerEvent(ExampleController sender);
        public static event ExampleControllerEvent Spawned;
        public static event ExampleControllerEvent BeingAttacked;
        public static event ExampleControllerEvent AttackStopped;

        [Tooltip("Amount of time to wait before moving away from Cubits.")]
        public float WaitTime = 3f;
        public Image Image { get { return image; } set { image = value; } }

        private Image image;
        private Shake shake = null;
        private bool isBeingAttacked = false;
        private BoxCollider2D col = null;

        // Use this for initialization
        void Start()
        {
            image = GetComponent<Image>();
            shake = GetComponent<Shake>();
            col = GetComponent<BoxCollider2D>();

            if (Spawned != null)
            {
                Spawned(this);
            }
        }

        private void OnTriggerEnter2D(Collider2D collision)
        {
            if (collision.name == "Cubits" && !shake.isActiveAndEnabled)
            {
                shake.enabled = true;
                isBeingAttacked = true;

                if (BeingAttacked != null)
                {
                    BeingAttacked(this);
                }
            }
        }

        private void OnTriggerExit2D(Collider2D collision)
        {
            if (collision.name == "Cubits" && shake.isActiveAndEnabled)
            {
                shake.enabled = false;
                isBeingAttacked = false;

                if (AttackStopped != null)
                {
                    AttackStopped(this);
                }

                col.enabled = false;
            }
        }
    }
}