using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(RectTransform))]
    public class Shake : MonoBehaviour
    {
        public Vector2 Speed = new Vector2(100f, 75f);
        public float Amount = 1.0f;

        new private RectTransform transform = null;

        private void Start()
        {
            transform = GetComponent<RectTransform>();
        }

        // Update is called once per frame
        private void Update()
        {
            Vector2 position = transform.anchoredPosition;
            position.x = Mathf.Sin(Time.time * Speed.x) * Amount;
            position.y = Mathf.Sin(Time.time * Speed.y) * Amount;

            transform.anchoredPosition = position;
        }
    }
}