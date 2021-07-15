package structure

import (
	"strconv"
)

type CustomDictionary map[string]interface{}

func (m CustomDictionary) JsonParseMap(s string) CustomDictionary {
	if val, ok := m[s]; ok && val != nil {
		return val.(map[string]interface{})
	}
	return make(map[string]interface{})
}

func (m CustomDictionary) JsonParseString(s string) string {
	if val, ok := m[s]; ok && val != nil {
		return val.(string)
	}
	return ""
}

func (m CustomDictionary) JsonParseFloat(s string) float64 {
	if val, ok := m[s]; ok && val != nil {
		return val.(float64)
	}
	return 0.0
}

func FloatToString(value float64) string {
	return strconv.FormatFloat(value, 'g', -1, 64)
}

//func CustomJsonUnmarshal(jsonStr string, )
