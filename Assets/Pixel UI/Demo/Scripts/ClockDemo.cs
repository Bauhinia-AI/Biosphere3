/******************************************************************************************
 * Name: ClockDemo.cs
 * Created by: Jeremy Voss
 * Created on: 03/01/2019
 * Last Modified: 04/29/2019
 * Description:
 * A simple script used in the demo to show off the new visual clock sprites.  The clock
 * is set to use real-time by default and will automatically adjust the image to a clear
 * day at the user's current real world time.  Unchecking use real time will update the
 * clock hour every second for a quicker preview of all the sprites.  Hovering over
 * the clock will always display the current real world time as a tooltip.  The current
 * weather sprite can be changed dynamically by clicking buttons within the scene.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Image))]
    public class ClockDemo : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler
    {
        [SerializeField]
        private UITooltip tooltipInstance = null;

        [SerializeField]
        private string clockResourcePath = string.Empty;
        [SerializeField]
        private Texture2D bloodMoon = null;
        [SerializeField]
        private Texture2D clear = null;
        [SerializeField]
        private Texture2D eclipse = null;
        [SerializeField]
        private Texture2D festival = null;
        [SerializeField]
        private Texture2D rainy = null;
        [SerializeField]
        private Texture2D snow = null;
        [SerializeField]
        private Texture2D stormy = null;
        [SerializeField]
        private Texture2D windy = null;
        [SerializeField]
        private float updateInterval = 1f;

        private bool useRealTime = true;
        private float timer = 0f;
        private Sprite[] sprites = null;
        private int index = 0;
        private bool tooltipActive = false;

        // Use this for initialization
        private void Start() {
            SetClearDay();
        }

        // Update is called once per frame
        private void Update() {
            timer += Time.deltaTime;
            if (timer >= updateInterval)
            {
                timer = 0f;
                if (sprites != null)
                {
                    if(tooltipActive)
                    {
                        UpdateTooltip();
                    }

                    if (useRealTime)
                    {
                        GetComponent<Image>().sprite = sprites[System.DateTime.Now.Hour];
                    }
                    else
                    {
                        index++;
                        if (index >= sprites.Length)
                        {
                            index = 0;
                        }
                        GetComponent<Image>().sprite = sprites[index];
                    }
                }
            }
        }

        public void UseRealTime(bool value)
        {
            useRealTime = value;
            if (!useRealTime)
            {
                index = System.DateTime.Now.Hour;
            }
            else
            {
                GetComponent<Image>().sprite = sprites[System.DateTime.Now.Hour];
            }
        }

        public void SetBloodMoonDay()
        {
            LoadSprites(bloodMoon);
        }

        public void SetClearDay()
        {
            LoadSprites(clear);
        }

        public void SetEclipseDay()
        {
            LoadSprites(eclipse);
        }

        public void SetFestivalDay()
        {
            LoadSprites(festival);
        }

        public void SetRainyDay()
        {
            LoadSprites(rainy);
        }

        public void SetSnowyDay()
        {
            LoadSprites(snow);
        }

        public void SetStormyDay()
        {
            LoadSprites(stormy);
        }

        public void SetWindyDay()
        {
            LoadSprites(windy);
        }

        public void OnPointerExit(PointerEventData eventData)
        {
            if(tooltipInstance == null)
            {
                return;
            }

            tooltipInstance.HideTooltip();
            tooltipActive = false;
        }

        public void OnPointerEnter(PointerEventData eventData)
        {
            if (tooltipInstance == null)
            {
                return;
            }

            UpdateTooltip();
            tooltipInstance.ShowTooltip();
            tooltipActive = true;
        }

        private void LoadSprites(Texture2D texture)
        {
            Sprite[] newSprites = Resources.LoadAll<Sprite>(clockResourcePath + texture.name);
            sprites = newSprites;
            if (useRealTime)
            {
                GetComponent<Image>().sprite = sprites[System.DateTime.Now.Hour];
            }
            else
            {
                GetComponent<Image>().sprite = sprites[index];
            }
        }

        private void UpdateTooltip()
        {
            tooltipInstance.SetText("The time in your world: " + System.DateTime.Now.ToString());
        }
    }
}