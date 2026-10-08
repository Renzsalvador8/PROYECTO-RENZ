// Minimal stand-ins for com.unity.test-framework types used by the PlayMode tests (compile-check only).
using System.Collections;
using System.Text.RegularExpressions;

namespace UnityEngine.TestTools
{
    [System.AttributeUsage(System.AttributeTargets.Method)]
    public sealed class UnityTestAttribute : NUnit.Framework.TestAttribute { }

    public static class LogAssert
    {
        public static bool ignoreFailingMessages { get; set; }
        public static void NoUnexpectedReceived() { }
        public static void Expect(LogType type, string message) { }
        public static void Expect(LogType type, Regex message) { }
    }
}
