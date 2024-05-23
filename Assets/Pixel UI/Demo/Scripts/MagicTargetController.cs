using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(RectTransform))]
    public class MagicTargetController : MonoBehaviour
    {
        public float ScreenWidth = 320;
        public float ScreenHeight = 180;

        new private RectTransform transform = null;

        private void Start()
        {
            transform = GetComponent<RectTransform>();
        }

        private void OnTriggerEnter2D(Collider2D collision)
        {
            if (collision.name == "Cubits")
            {
                float newX = Random.Range(-(ScreenWidth / 2f), (ScreenWidth / 2f));
                float newY = Random.Range(-(ScreenHeight / 2f), (ScreenHeight / 2f));
                transform.anchoredPosition = new Vector2(newX, newY);
            }
        }
    }
}