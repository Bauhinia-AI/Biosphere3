/******************************************************************************************
 * Name: PingPong.cs
 * Created by: Jeremy Voss
 * Created on: 01/15/2019
 * Last Modified: 01/16/2019
 * Description:
 * A script that ping pongs a slider value between 0 and 1.
 ******************************************************************************************/
using UnityEngine;
using UnityEngine.UI;

namespace PixelsoftGames.PixelUI
{
    [RequireComponent(typeof(Slider))]
    public class PingPong : MonoBehaviour
    {
        #region Fields & Properties

        Slider slider;

        #endregion

        #region Monobehaviour Callbacks

        private void Awake()
        {
            slider = GetComponent<Slider>();
        }

        private void Update()
        {
            slider.value = Mathf.PingPong(Time.time, 1);
        }

        #endregion
    }
}