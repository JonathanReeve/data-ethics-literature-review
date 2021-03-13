{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}

module Main where

import Data.RDF
import Text.RDF.RDF4H.TurtleParser
import Text.RDF.RDF4H.TurtleSerializer

import Control.Applicative
import qualified Data.ByteString.Lazy as BL
import Data.Csv
import qualified Data.Vector as V

-- COURSE TITLE,CODE,UNIVERSITY,DEPARTMENT,INSTRUCTOR,LEVEL,
-- COURSE DESCRIPTION - URL,SYLLABUS ,ADDITIONAL URLs,LAST UPDATED,REQUEST BY EMAIL,LANGUAGE,Sub-Topic,REQUIREMENT?,NOTES,CONTROL

data Course = Course
    { title   :: String
    , code    :: String
    , university    :: String
    , department    :: String
    , instructor    :: String
    , level    :: String
    , url    :: String
    , syllabus    :: String
    , moreURLs    :: String
    , lastUpdated    :: String
    , requestByEmail    :: String
    , language :: String
    , subTopic :: String
    , requirement :: String
    , notes :: String
    , control :: String
    }

valueParse :: NamedRecord -> Parser Course
valueParse r = Course <$> r .: "COURSE TITLE" <*> r .: "CODE"
                                              <*> r .: "UNIVERSITY"
                                              <*> r .: "DEPARTMENT"
                                              <*> r .: "INSTRUCTOR"
                                              <*> r .: "LEVEL"
                                              <*> r .: "COURSE DESCRIPTION - URL"
                                              <*> r .: "SYLLABUS "
                                              <*> r .: "ADDITIONAL URLs"
                                              <*> r .: "LAST UPDATED"
                                              <*> r .: "REQUEST BY EMAIL"
                                              <*> r .: "LANGUAGE"
                                              <*> r .: "Sub-Topic"
                                              <*> r .: "REQUIREMENT?"
                                              <*> r .: "NOTES"
                                              <*> r .: "CONTROL"

main :: IO ()
main = do
    csvData <- BL.readFile "tech-ethics-courses.csv"
    case decodeByNameWithP valueParse defaultDecodeOptions csvData of
        Left err -> putStrLn err
        Right (_, v) -> V.forM_ v $ \ p ->
            putStrLn $ title p ++ " titleOf " ++ (code p) ++ " code"
