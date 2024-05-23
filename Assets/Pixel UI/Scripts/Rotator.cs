/******************************************************************************************
 * Name: Rotator.cs
 * Created by: Jeremy Voss
 * Created on: 9/12/2018
 * Last Modified: 9/12/2018
 * Owned by: Pixelsoft Games, LLC.
 * Description:
 * A very basic script designed to rotate the Pixelsoft Games logo cube in the demo scene.
 ******************************************************************************************/
using UnityEngine;

namespace PixelsoftGames.PixelUI
{
    public class Rotator : MonoBehaviour
    {
        #region Private Serialized Variables

        /// <summary>
        /// How fast to rotate the game object.
        /// </summary>
        [Tooltip("Speed at which we will rotate the object.")]
        [SerializeField]
        private float rotationSpeed = 0f;

        #endregion

        #region Monobehaviour Callbacks

        // Update is called once per frame
        private void Update()
        {
            transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime);
        }

        #endregion
    }
}