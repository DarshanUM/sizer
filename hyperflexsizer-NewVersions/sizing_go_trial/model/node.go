package model

import (
	"cisco_sizer/structure"
	"fmt"
	"time"

	"github.com/jinzhu/gorm"
)

type Node struct {
	ID            int            `gorm:"primaryKey"`
	Name          string         `gorm:"size:500" db:"name" json:"name,omitempty"`
	SortIndex     int            `gorm:"default:5000" db:"sort_index" json:"sort_index,omitempty"`
	HerculesAvail bool           `gorm:"default:false" db:"hercules_avail" json:"hercules_avail,omitempty"`
	HxBoostAvail  bool           `gorm:"default:false" db:"hx_boost_avail" json:"hx_boost_avail,omitempty"`
	NodeJson      structure.JSON `sql:"type:json" db:"node_json" json:"node_json,omitempty"`
	Type          string         `gorm:"size:200" db:"type" json:"type,omitempty"`
	Status        bool           `gorm:"default:true" db:"status" json:"status,omitempty"`
	CreatedDate   time.Time      `sql:"DEFAULT:current_timestamp;type:datetime" db:"created_date" json:"created_date,omitempty"`
	UpdatedDate   time.Time      `sql:"DEFAULT:current_timestamp;type:datetime" db:"updated_date" json:"updated_date,omitempty"`
}

// TableName overrides the table name used by User to `profiles`
func (Node) TableName() string {
	return "hyperconverged_node"
}

func GetFirstNode(db *gorm.DB, node *Node) (err error) {
	err = db.First(node).Error
	if err != nil {
		return err
	}
	return nil
}

func GetAllNode(db *gorm.DB, node *[]Node) (err error) {
	err = db.Find(node).Error
	if err != nil {
		return err
	}
	return nil
}

func GetAllNodesWithStatus(db *gorm.DB, nodes *[]Node, status bool) (err error) {
	err = db.Where("status = ?", status).Find(&nodes).Error
	if err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}

//example ::: SELECT * FROM users WHERE name IN ('jinzhu','jinzhu 2');
func GetNodeByMultipleName(db *gorm.DB, node *[]Node, nodeNames []string) (err error) {
	//db.Find(node, []int{1, 2, 3})
	err = db.Where("`name` IN ( ? ) ", nodeNames).Find(node).Error
	// err = db.Where("`name` IN (\"HXAF-240M5SX\",\"HX-C240-M5SX [CTO]\")").Find(node).Error
	if err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}
