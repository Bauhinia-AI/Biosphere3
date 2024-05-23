using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(RectTransform))]
    public class PanelController : MonoBehaviour
    {
        public float MoveSpeed = 8f;
        public Vector2 MoveOffset;

        new private RectTransform transform = null;
        public RectTransform GetTransform { get { return transform; } }

        private bool isMoving = false;
        private Vector2 TargetPosition;

        private void Start()
        {
            transform = GetComponent<RectTransform>();
        }

        public void Move()
        {
            isMoving = true;
            TargetPosition = transform.anchoredPosition + MoveOffset;
        }

        private void Update()
        {
            if (isMoving)
            {
                transform.anchoredPosition = Vector2.MoveTowards(transform.anchoredPosition, TargetPosition, MoveSpeed * Time.deltaTime);
            }
        }
    }
}