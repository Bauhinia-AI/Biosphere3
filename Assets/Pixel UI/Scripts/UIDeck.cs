/******************************************************************************************
 * Name: UIDeck.cs
 * Created by: Jeremy Voss
 * Created on: 03/01/2019
 * Last Modified: 04/29/2019
 * Description:
 * A simple script that can be used to manage the creation of UI Cards.  This example
 * script simply creates cards from hard-coded data.  However, you could modify the
 * script to use your own data structure.  A good example of the deck script might
 * be to keep track of cards it has dealt out, etc.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    #region Enums

    public enum CardTypes { Item, Travel, Shop, Action, Quality, Relationship }

    #endregion

    public class UIDeck : MonoBehaviour
    {
        #region Fields & Properties

        [SerializeField]
        [Tooltip("Card profile used for creating cards.")]
        private CardProfile primaryCardProfile = null;

        [SerializeField]
        [Tooltip("The image used by the card deck.")]
        private Image deckImage = null;

        private GameObject activeCard = null;

        [Tooltip("DEMO ONLY")]
        public Sprite DemoSprite1 = null, DemoSprite2 = null, DemoSprite3 = null, DemoSprite4 = null, DemoSprite5 = null, DemoSprite6 = null;

        #endregion

        #region Monobehavior Callbacks

        // Use this for initialization
        private void Start()
        {
            LoadCardProfile();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Replaces the deck image with a custom sprite.
        /// </summary>
        /// <param name="sprite">The sprite to represent the deck image.</param>
        public void LoadCustomDeckImage(Sprite sprite)
        {
            if (deckImage != null && sprite != null)
            {
                deckImage.sprite = sprite;
            }
        }

        /// <summary>
        /// Loads the default deck sprite from data.
        /// </summary>
        public void LoadDefaultDeckImage()
        {
            if (deckImage != null && primaryCardProfile != null && primaryCardProfile.CardDeckSprite != null)
            {
                deckImage.sprite = primaryCardProfile.CardDeckSprite;
            }
        }

        /// <summary>
        /// Creates an action type card using hard-coded data.
        /// </summary>
        public void CreateActionCard()
        {
            CreateCard(transform, CardTypes.Action);
            if (activeCard == null)
            {
                return;
            }

            activeCard.transform.SetParent(transform.parent.parent);
            UICard card = activeCard.GetComponent<UICard>();
            card.Icon.sprite = DemoSprite1;
            card.Name.text = "Chop";
            card.Description.text = "Strike the nearest tree with an axe.";
            card.Modifier.text = "15";
        }

        /// <summary>
        /// Creates an item type card using hard-coded data.
        /// </summary>
        public void CreateItemCard()
        {
            CreateCard(transform, CardTypes.Item);
            if (activeCard == null)
            {
                return;
            }

            activeCard.transform.SetParent(transform.parent.parent);
            UICard card = activeCard.GetComponent<UICard>();
            card.Icon.sprite = DemoSprite2;
            card.Name.text = "Copper Axe";
            card.Description.text = "An axe made from copper.  Weak, but useful.";
            card.Modifier.text = "1";
        }

        /// <summary>
        /// Creates a shop type card using hard-coded data.
        /// </summary>
        public void CreateShopCard()
        {
            CreateCard(transform, CardTypes.Shop);
            if (activeCard == null)
            {
                return;
            }

            activeCard.transform.SetParent(transform.parent.parent);
            UICard card = activeCard.GetComponent<UICard>();
            card.Icon.sprite = DemoSprite3;
            card.Name.text = "Wood";
            card.Description.text = "A sturdy piece of wood used for crafting.";
            card.Modifier.text = "50";
        }

        /// <summary>
        /// Creates a travel type card using hard-coded data.
        /// </summary>
        public void CreateTravelCard()
        {
            CreateCard(transform, CardTypes.Travel);
            if (activeCard == null)
            {
                return;
            }

            activeCard.transform.SetParent(transform.parent.parent);
            UICard card = activeCard.GetComponent<UICard>();
            card.Icon.sprite = DemoSprite4;
            card.Name.text = "Demo Village";
            card.Description.text = "A humble village on the outskirts of Pixel UI";
            card.Modifier.text = "45";
        }

        /// <summary>
        /// Creates a quality type card using hard-coded data.
        /// </summary>
        public void CreateQualityCard()
        {
            CreateCard(transform, CardTypes.Quality);
            if (activeCard == null)
            {
                return;
            }

            activeCard.transform.SetParent(transform.parent.parent);
            UICard card = activeCard.GetComponent<UICard>();
            card.Icon.sprite = DemoSprite5;
            card.Name.text = "Common Mushroom";
            card.Description.text = "A common mushroom in the world of Pixel UI.";
            card.Modifier.text = string.Empty;
        }

        /// <summary>
        /// Creates a heart type card using hard-coded data.
        /// </summary>
        public void CreateHeartCard()
        {
            CreateCard(transform, CardTypes.Relationship);
            if (activeCard == null)
            {
                return;
            }

            activeCard.transform.SetParent(transform.parent.parent);
            UICard card = activeCard.GetComponent<UICard>();
            card.Icon.sprite = DemoSprite6;
            card.Name.text = "Dire Pixel";
            card.Description.text = "The pixel artist for Pixel UI.";
            card.Modifier.text = string.Empty;
        }

        /// <summary>
        /// Moves the active card to a hard coded position.
        /// </summary>
        public void MoveCard()
        {
            if(activeCard == null || primaryCardProfile == null)
            {
                return;
            }

            activeCard.GetComponent<UICard>().MoveToPosition(Vector3.zero, false, false, primaryCardProfile.Move_Duration);
        }

        /// <summary>
        /// Flips over the active card.
        /// </summary>
        public void FlipCard()
        {
            if (activeCard == null || primaryCardProfile == null)
            {
                return;
            }

            activeCard.GetComponent<UICard>().Flip(primaryCardProfile.Flip_Duration, primaryCardProfile.Fade_Duration);
        }

        /// <summary>
        /// Peeks at the active card.
        /// </summary>
        public void PeekCard()
        {
            if (activeCard == null || primaryCardProfile == null)
            {
                return;
            }

            activeCard.GetComponent<UICard>().Peek(primaryCardProfile.Flip_Duration, primaryCardProfile.Fade_Duration, primaryCardProfile.Peek_Duration);
        }

        #endregion

        #region Private Methods

        /// <summary>
        /// Loads default deck image based on present card profile.
        /// </summary>
        private void LoadCardProfile()
        {
            if (primaryCardProfile == null)
            {
                return;
            }

            LoadDefaultDeckImage();
        }

        /// <summary>
        /// Creates a new card, destroying the old active card, and setting the new card as the active one.
        /// </summary>
        /// <param name="parent">The transform parent for the new card.</param>
        /// <param name="type">The type of card we need to create.</param>
        private void CreateCard(Transform parent, CardTypes type)
        {
            if (primaryCardProfile == null || primaryCardProfile.CardPrefab == null)
            {
                return;
            }

            DestroyActiveCard();
            activeCard = Instantiate(primaryCardProfile.CardPrefab, parent, false);
            UICard uiCard = activeCard.GetComponent<UICard>();
            uiCard.cardBackSprite = primaryCardProfile.CardBackSprite;
            uiCard.cardFrontSprite = primaryCardProfile.CardFrontSprite;
            uiCard.Background.sprite = primaryCardProfile.CardBackSprite;

            switch (type)
            {
                case CardTypes.Action: // Energy
                    uiCard.Foreground.sprite = primaryCardProfile.EnergyForegroundSprite;
                    break;
                case CardTypes.Item: // Inventory
                    uiCard.Foreground.sprite = primaryCardProfile.InventoryForegroundSprite;
                    break;
                case CardTypes.Quality: // Quality
                    uiCard.Foreground.sprite = primaryCardProfile.StarForegroundSprites[Random.Range(0, primaryCardProfile.StarForegroundSprites.Count)];
                    break;
                case CardTypes.Relationship: // Relationship
                    uiCard.Foreground.sprite = primaryCardProfile.HeartForegroundSprites[Random.Range(0, primaryCardProfile.HeartForegroundSprites.Count)];
                    break;
                case CardTypes.Shop: // Shop
                    uiCard.Foreground.sprite = primaryCardProfile.ShopForegroundSprite;
                    break;
                case CardTypes.Travel: // Time
                    uiCard.Foreground.sprite = primaryCardProfile.TimeForegroundSprite;
                    break;
            }
        }

        /// <summary>
        /// Destroys the currently active card.
        /// </summary>
        private void DestroyActiveCard()
        {
            if (activeCard != null)
            {
                Destroy(activeCard);
            }
        }

        #endregion
    }
}