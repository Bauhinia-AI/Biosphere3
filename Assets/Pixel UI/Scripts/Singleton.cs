using UnityEngine;

namespace PixelsoftGames
{
    /// <summary>
    /// Singleton
    /// </summary>
    public class Singleton<T> : MonoBehaviour where T : Component
    {
        protected static T instance;

        /// <summary>
        /// Singleton design pattern
        /// </summary>
        public static T Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<T>();
                    if (instance == null)
                    {
                        GameObject obj = new GameObject();
                        instance = obj.AddComponent<T>();
                    }
                }

                return instance;
            }
        }

        /// <summary>
        /// On awake, check if there's already an existing instance of this Singleton.  If there is, then destroy this instance.
        /// </summary>
        public virtual void Awake()
        {
            if (!Application.isPlaying)
            {
                return;
            }

            // Check if a Singleton instance already exists
            if (instance == null)
            {
                // If none exists, make this the Singleton
                instance = this as T;
                DontDestroyOnLoad(transform.gameObject);
                enabled = true;
            }
            else
            {
                // If another Singleton instance already exists, destroy this instance.
                if (this != instance)
                {
                    Destroy(this.gameObject);
                }
            }
        }

        /// <summary>
        /// On destroy check if we are destroying the singleton instance.  If so, we want to ensure that we nullify the instance reference.
        /// </summary>
        public virtual void OnDestroy()
        {
            if(instance != null && instance == this)
            {
                instance = null;
            }
        }
    }
}