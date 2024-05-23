/******************************************************************************************
 * Name: UIExperienceBar.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 02/24/2019
 * Description:
 * This script serves 2 purposes.  The first is to manage the experience bar, while the
 * second manages the experience table.  Tweaking the settings from the inspector will
 * result in the creation of a unique exp table for your settings when the script executes
 * in runtime.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Slider))]
    public class UIExperienceBar : MonoBehaviour
    {
        #region Events

        public delegate void ExperienceBarEvent(UIExperienceBar expBar);
        /// <summary>
        /// This event gets called when enough experience points have
        /// been accumulated to level up the bar.
        /// </summary>
        public static event ExperienceBarEvent LevelUp;

        #endregion

        #region Fields & Properties

        [SerializeField]
        [Range(1, 1000)]
        [Tooltip("The default level to begin with (i.e. - we start the game as a level 1 player)")]
        private int DefaultLevel = 1;
        [SerializeField]
        [Range(1, 1000)]
        [Tooltip("The maximum possible level that can be achieved.")]
        private int MaximumLevel = 100;
        [SerializeField]
        [Tooltip("The base experience required to gain the first level")]
        private int BaseExperience = 1000;
        [SerializeField]
        [Tooltip("How should the exp required to level for each level be staggered")]
        private float TableStagger = 1.5f;

        private int[] expTable = null;
        private int currentExperienceTowardsLevel = 0;
        private int currentLevel = 0;
        private Slider slider = null;

        /// <summary>
        /// Returns the amount of experience points earned towards the next level.
        /// </summary>
        public int GetExperienceTowardsLevel { get { return currentExperienceTowardsLevel; } }
        /// <summary>
        /// Returns the amount of experience points still required to level up.
        /// </summary>
        public int GetExperienceToNextLevel { get { return expTable[currentLevel - 1] - currentExperienceTowardsLevel; } }
        /// <summary>
        /// Returns the current level.
        /// </summary>
        public int GetCurrentLevel { get { return currentLevel; } }
        /// <summary>
        /// This method will return the total amount of experience points earned.
        /// </summary>
        public int GetTotalExperience
        {
            get
            {
                int total = 0;

                for (int i = 0; i < currentLevel; i++)
                    total += expTable[i];
                total += currentExperienceTowardsLevel;

                return total;
            }
        }

        #endregion

        #region Monobehaviour Callbacks

        private void Awake()
        {
            slider = GetComponent<Slider>();
        }

        // Use this for initialization
        private void Start()
        {
            currentLevel = DefaultLevel;
            CreateTable();
            UpdateValue();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// This method will grant experience points in the given amount of fire a level up event if necessary.
        /// </summary>
        /// <param name="amount">The amount of experience to gain.</param>
        /// <param name="suppressEvent">Should the level up event be silenced?</param>
        public void GiveExperiencePoints(int amount, bool suppressEvent = false)
        {
            currentExperienceTowardsLevel += amount;

            while (currentExperienceTowardsLevel >= expTable[currentLevel - 1])
            {
                currentExperienceTowardsLevel -= expTable[currentLevel - 1];
                currentLevel++;
            }

            if (!suppressEvent && LevelUp != null)
            {
                LevelUp(this);
            }

            UpdateValue();
        }

        /// <summary>
        /// This method will return the total amount of experience points earned.
        /// </summary>
        /// <returns></returns>
        [System.Obsolete("GetTotalExperiencePoints has been deprecated, please use GetTotalExperience instead.")]
        public int GetTotalExperiencePoints()
        {
            int total = 0;

            for (int i = 0; i < currentLevel; i++)
            {
                total += expTable[i];
            }
            total += currentExperienceTowardsLevel;

            return total;
        }

        #endregion

        #region Private Methods

        /// <summary>
        /// This method will create an experience points table from level 1 to the maximum level.
        /// </summary>
        private void CreateTable()
        {
            expTable = new int[MaximumLevel];
            for (int i = 0; i < expTable.Length; i++)
            {
                expTable[i] = Mathf.FloorToInt(BaseExperience * Mathf.Pow(i + 1, TableStagger));
            }
        }

        /// <summary>
        /// This will update the slider experience point value.
        /// </summary>
        private void UpdateValue()
        {
            slider.value = (float)currentExperienceTowardsLevel / expTable[currentLevel - 1];
        }

        #endregion
    }
}