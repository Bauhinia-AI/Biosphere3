/******************************************************************************************
 * Name: CardProfile.cs
 * Created by: Jeremy Voss
 * Created on: 03/01/2019
 * Last Modified: 04/29/2019
 * Description:
 * A handy script used to create a scriptable object data asset that stores pixel card
 * presets.  Useful for when you have multiple decks using different sprites that require
 * different settings.
 ******************************************************************************************/
using System.Collections.Generic;
using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    [CreateAssetMenu(fileName = "New Card Profile", menuName = "Pixel UI/Card Profile")]
    public class CardProfile : ScriptableObject
    {
        #region Fields & Properties

        [Tooltip("The prefab to use when instantiating cards.")]
        public GameObject CardPrefab = null;
        [Tooltip("The sprite displayed behind a card or deck (typically a black card outline).")]
        public Sprite CardBlankSprite = null;
        [Tooltip("The sprite used to represent the card deck.")]
        public Sprite CardDeckSprite = null;
        [Tooltip("The sprite used to represent the back of the card.")]
        public Sprite CardBackSprite = null;
        [Tooltip("The sprite used to represent the front of the card.")]
        public Sprite CardFrontSprite = null;
        [Tooltip("The sprite to use for displaying inventory (crate) foreground.")]
        public Sprite InventoryForegroundSprite = null;
        [Tooltip("The sprite to use for displaying shop (coin) foreground.")]
        public Sprite ShopForegroundSprite = null;
        [Tooltip("The sprite to use for displaying the time (hourglass) foreground.")]
        public Sprite TimeForegroundSprite = null;
        [Tooltip("The sprite to use for displaying the energy (lightning bolt) foreground.")]
        public Sprite EnergyForegroundSprite = null;
        [Tooltip("The sprites to use for displaying hearts (relationship).")]
        public List<Sprite> HeartForegroundSprites = null;
        [Tooltip("The sprites to use for displaying stars (quality).")]
        public List<Sprite> StarForegroundSprites = null;
        [Tooltip("How long it takes to flip a card over.")]
        public float Flip_Duration = 1f;
        [Tooltip("How long we wait for a card to fade in/out.")]
        public float Fade_Duration = 1f;
        [Tooltip("How long we allow a card to be peeked at.")]
        public float Peek_Duration = 5f;
        [Tooltip("How long it takes a card to move to its desired position.")]
        public float Move_Duration = 1f;

        #endregion
    }
}