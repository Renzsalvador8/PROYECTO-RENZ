using TheTester.Core;

namespace TheTester
{
    public enum GameScene { MainMenu = 0, Showroom = 1, TestDrive = 2, ZenithStudio = 3 }

    public static class GameScenes
    {
        public static string SceneName(GameScene s)
        {
            switch (s)
            {
                case GameScene.Showroom: return "01_Showroom";
                case GameScene.TestDrive: return "02_TestDrive";
                case GameScene.ZenithStudio: return "03_ZenithStudio";
                default: return "00_MainMenu";
            }
        }

        /// <summary>Scene a saved chapter resumes in.</summary>
        public static GameScene ForChapter(Chapter c)
        {
            switch (c)
            {
                case Chapter.TestDrive: return GameScene.TestDrive;
                case Chapter.ZenithStudio:
                case Chapter.Completed: return GameScene.ZenithStudio;
                case Chapter.NewGame: return GameScene.Showroom;
                default: return GameScene.Showroom;
            }
        }
    }
}
