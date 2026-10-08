using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace TheTester.Core
{
    /// <summary>
    /// Minimal JSON DOM used for the game's data files (levels, rigs, clips, hotspots).
    /// Kept dependency-free so it can be unit tested outside Unity.
    /// </summary>
    public sealed class JsonNode
    {
        public enum Kind { Null, Bool, Number, String, Array, Object }

        public Kind Type { get; private set; }
        private bool _bool;
        private double _number;
        private string _string;
        private List<JsonNode> _array;
        private Dictionary<string, JsonNode> _object;
        private List<string> _keys;

        public static readonly JsonNode Null = new JsonNode { Type = Kind.Null };

        public bool IsNull => Type == Kind.Null;
        public int Count => Type == Kind.Array ? _array.Count : Type == Kind.Object ? _object.Count : 0;
        public IList<JsonNode> Items => _array ?? (IList<JsonNode>)Array.Empty<JsonNode>();
        public IList<string> Keys => _keys ?? (IList<string>)Array.Empty<string>();

        public JsonNode this[string key]
        {
            get
            {
                if (Type == Kind.Object && _object.TryGetValue(key, out var v)) return v;
                return Null;
            }
        }

        public JsonNode this[int index]
        {
            get
            {
                if (Type == Kind.Array && index >= 0 && index < _array.Count) return _array[index];
                return Null;
            }
        }

        public bool Has(string key) => Type == Kind.Object && _object.ContainsKey(key);

        public float AsFloat(float fallback = 0f) => Type == Kind.Number ? (float)_number : Type == Kind.Bool ? (_bool ? 1f : 0f) : fallback;
        public double AsDouble(double fallback = 0) => Type == Kind.Number ? _number : fallback;
        public int AsInt(int fallback = 0) => Type == Kind.Number ? (int)Math.Round(_number) : fallback;
        public bool AsBool(bool fallback = false) => Type == Kind.Bool ? _bool : Type == Kind.Number ? _number != 0 : fallback;
        public string AsString(string fallback = "") => Type == Kind.String ? _string : Type == Kind.Number ? _number.ToString(CultureInfo.InvariantCulture) : fallback;

        public float GetFloat(string key, float fallback = 0f) => Has(key) ? this[key].AsFloat(fallback) : fallback;
        public int GetInt(string key, int fallback = 0) => Has(key) ? this[key].AsInt(fallback) : fallback;
        public string GetString(string key, string fallback = "") => Has(key) ? this[key].AsString(fallback) : fallback;
        public bool GetBool(string key, bool fallback = false) => Has(key) ? this[key].AsBool(fallback) : fallback;

        /// <summary>Reads a numeric array into floats (missing entries keep the fallback values).</summary>
        public float[] AsFloats(params float[] fallback)
        {
            if (Type != Kind.Array) return fallback;
            int n = Math.Max(_array.Count, fallback?.Length ?? 0);
            var r = new float[n];
            for (int i = 0; i < n; i++)
                r[i] = i < _array.Count ? _array[i].AsFloat(i < fallback.Length ? fallback[i] : 0f) : fallback[i];
            return r;
        }

        // ------------------------------------------------------------------ parsing
        public static JsonNode Parse(string text)
        {
            if (text == null) throw new ArgumentNullException(nameof(text));
            var p = new Parser(text);
            p.SkipWs();
            var node = p.ParseValue();
            p.SkipWs();
            if (!p.End) throw new FormatException("Unexpected trailing characters at " + p.Pos);
            return node;
        }

        public static JsonNode FromNumber(double v) => new JsonNode { Type = Kind.Number, _number = v };
        public static JsonNode FromString(string v) => new JsonNode { Type = Kind.String, _string = v };
        public static JsonNode FromBool(bool v) => new JsonNode { Type = Kind.Bool, _bool = v };

        public static JsonNode NewObject()
        {
            return new JsonNode { Type = Kind.Object, _object = new Dictionary<string, JsonNode>(), _keys = new List<string>() };
        }

        public static JsonNode NewArray() => new JsonNode { Type = Kind.Array, _array = new List<JsonNode>() };

        public void Set(string key, JsonNode value)
        {
            if (Type != Kind.Object) throw new InvalidOperationException("Not an object");
            if (!_object.ContainsKey(key)) _keys.Add(key);
            _object[key] = value ?? Null;
        }

        public void Add(JsonNode value)
        {
            if (Type != Kind.Array) throw new InvalidOperationException("Not an array");
            _array.Add(value ?? Null);
        }

        public override string ToString()
        {
            var sb = new StringBuilder();
            Write(sb);
            return sb.ToString();
        }

        private void Write(StringBuilder sb)
        {
            switch (Type)
            {
                case Kind.Null: sb.Append("null"); break;
                case Kind.Bool: sb.Append(_bool ? "true" : "false"); break;
                case Kind.Number: sb.Append(_number.ToString("R", CultureInfo.InvariantCulture)); break;
                case Kind.String: WriteString(sb, _string); break;
                case Kind.Array:
                    sb.Append('[');
                    for (int i = 0; i < _array.Count; i++)
                    {
                        if (i > 0) sb.Append(',');
                        _array[i].Write(sb);
                    }
                    sb.Append(']');
                    break;
                case Kind.Object:
                    sb.Append('{');
                    for (int i = 0; i < _keys.Count; i++)
                    {
                        if (i > 0) sb.Append(',');
                        WriteString(sb, _keys[i]);
                        sb.Append(':');
                        _object[_keys[i]].Write(sb);
                    }
                    sb.Append('}');
                    break;
            }
        }

        private static void WriteString(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4"));
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
        }

        private sealed class Parser
        {
            private readonly string _s;
            public int Pos;
            public Parser(string s) { _s = s; Pos = 0; }
            public bool End => Pos >= _s.Length;

            public void SkipWs()
            {
                while (Pos < _s.Length && char.IsWhiteSpace(_s[Pos])) Pos++;
            }

            public JsonNode ParseValue()
            {
                SkipWs();
                if (End) throw new FormatException("Unexpected end of JSON");
                char c = _s[Pos];
                switch (c)
                {
                    case '{': return ParseObject();
                    case '[': return ParseArray();
                    case '"': return FromString(ParseString());
                    case 't': Expect("true"); return FromBool(true);
                    case 'f': Expect("false"); return FromBool(false);
                    case 'n': Expect("null"); return Null;
                    default:
                        if (c == '-' || (c >= '0' && c <= '9')) return ParseNumber();
                        throw new FormatException("Unexpected character '" + c + "' at " + Pos);
                }
            }

            private void Expect(string word)
            {
                if (string.CompareOrdinal(_s, Pos, word, 0, word.Length) != 0)
                    throw new FormatException("Expected '" + word + "' at " + Pos);
                Pos += word.Length;
            }

            private JsonNode ParseObject()
            {
                var node = NewObject();
                Pos++; // {
                SkipWs();
                if (!End && _s[Pos] == '}') { Pos++; return node; }
                while (true)
                {
                    SkipWs();
                    if (End || _s[Pos] != '"') throw new FormatException("Expected key at " + Pos);
                    string key = ParseString();
                    SkipWs();
                    if (End || _s[Pos] != ':') throw new FormatException("Expected ':' at " + Pos);
                    Pos++;
                    node.Set(key, ParseValue());
                    SkipWs();
                    if (End) throw new FormatException("Unterminated object");
                    if (_s[Pos] == ',') { Pos++; continue; }
                    if (_s[Pos] == '}') { Pos++; return node; }
                    throw new FormatException("Expected ',' or '}' at " + Pos);
                }
            }

            private JsonNode ParseArray()
            {
                var node = NewArray();
                Pos++; // [
                SkipWs();
                if (!End && _s[Pos] == ']') { Pos++; return node; }
                while (true)
                {
                    node.Add(ParseValue());
                    SkipWs();
                    if (End) throw new FormatException("Unterminated array");
                    if (_s[Pos] == ',') { Pos++; continue; }
                    if (_s[Pos] == ']') { Pos++; return node; }
                    throw new FormatException("Expected ',' or ']' at " + Pos);
                }
            }

            private string ParseString()
            {
                var sb = new StringBuilder();
                Pos++; // opening quote
                while (true)
                {
                    if (End) throw new FormatException("Unterminated string");
                    char c = _s[Pos++];
                    if (c == '"') return sb.ToString();
                    if (c != '\\') { sb.Append(c); continue; }
                    if (End) throw new FormatException("Bad escape");
                    char e = _s[Pos++];
                    switch (e)
                    {
                        case '"': sb.Append('"'); break;
                        case '\\': sb.Append('\\'); break;
                        case '/': sb.Append('/'); break;
                        case 'b': sb.Append('\b'); break;
                        case 'f': sb.Append('\f'); break;
                        case 'n': sb.Append('\n'); break;
                        case 'r': sb.Append('\r'); break;
                        case 't': sb.Append('\t'); break;
                        case 'u':
                            if (Pos + 4 > _s.Length) throw new FormatException("Bad unicode escape");
                            sb.Append((char)Convert.ToInt32(_s.Substring(Pos, 4), 16));
                            Pos += 4;
                            break;
                        default: throw new FormatException("Bad escape '\\" + e + "'");
                    }
                }
            }

            private JsonNode ParseNumber()
            {
                int start = Pos;
                if (_s[Pos] == '-') Pos++;
                while (Pos < _s.Length && "0123456789.eE+-".IndexOf(_s[Pos]) >= 0) Pos++;
                string num = _s.Substring(start, Pos - start);
                if (!double.TryParse(num, NumberStyles.Float, CultureInfo.InvariantCulture, out double v))
                    throw new FormatException("Bad number '" + num + "'");
                return FromNumber(v);
            }
        }
    }
}
