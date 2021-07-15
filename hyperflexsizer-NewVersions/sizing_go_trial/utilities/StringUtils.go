package utilities

import (
	"fmt"
)

func StringInSlice(a string, list []string) bool {
	for _, b := range list {
		if b == a {
			return true
		}
	}
	return false
}

func All(array []string, val string) bool {
	for _, value := range array {
		if val != value {
			return false
		}
	}
	return true
}

func Any(array []string, val string) bool {
	for _, value := range array {
		if val == value {
			return true
		}
	}
	return false
}

func SliceInterfaceToSliceString(slice_interface []interface{}) []string {
	slice_string := make([]string, len(slice_interface))
	for i, v := range slice_interface {
		slice_string[i] = fmt.Sprint(v)
	}
	return slice_string
}

func TestEq(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func RemoveDuplicateValuesString(stringSlice []string) []string {
	keys := make(map[string]bool)
	list := []string{}

	for _, entry := range stringSlice {
		if _, value := keys[entry]; !value {
			keys[entry] = true
			list = append(list, entry)
		}
	}
	return list
}
