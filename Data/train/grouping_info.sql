  case when Pclass <= 1.0 then 1.00391595551
       when Pclass > 1.0 and Pclass <= 2.0 then 0.364484844598
       when Pclass > 2.0 then -0.666482656715
       else 0.0000 end as Pclass_woe
 ,case when Sex = male then -0.983832709242
       when Sex = female then 1.52987700334
       else 0.0000 end as Sex_woe
 ,case when SibSp <= 0.0 then -0.16605677012
       when SibSp > 0.0 and SibSp <= 3.0 then 0.512818543204
       when SibSp > 3.0 then -1.72393687289
       else 0.0000 end as SibSp_woe
 ,case when Parch <= 0.0 then -0.173748124154
       when Parch > 0.0 then 0.520244687535
       else 0.0000 end as Parch_woe
 ,case when Fare <= 7.225 then -1.62677312444
       when Fare > 7.225 and Fare <= 10.5 then -0.750487727175
       when Fare > 10.5 and Fare <= 77.9583 then 0.286808137504
       when Fare > 77.9583 then 1.61842000875
       else 0.0000 end as Fare_woe
